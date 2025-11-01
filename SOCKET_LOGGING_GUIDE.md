# Socket Reconnection & Event Tracking - Logging Guide

## Overview
Enhanced logging has been added to `api/pages/ipersona/socket/ipersona_socket.py` to track:
- Client connections/disconnections
- SID changes during reconnection
- Event emission ("interview done", etc.)
- Message queuing and delivery

## Key Log Patterns to Watch

### 1. Connection Events

#### New Connection
```
================================================================================
[CONNECT][2025-10-30 22:34:26.123] NEW CONNECTION - SID: abc123xyz
================================================================================
[CONNECT][USER_MAPPING] Processing user_id mapping for user: 1688
[CONNECT][NEW_SESSION] User 1688 - First connection with SID=abc123xyz
[CONNECT][ROOM] Joined user room: user_1688
```

#### Reconnection (SID Change)
```
================================================================================
[CONNECT][2025-10-30 22:35:15.456] NEW CONNECTION - SID: xyz789new
================================================================================
[CONNECT][USER_MAPPING] Processing user_id mapping for user: 1688
[CONNECT][RECONNECTION] User 1688 reconnecting: OLD SID=abc123xyz -> NEW SID=xyz789new
[CONNECT][ROOM] Joined user room: user_1688
```

### 2. Disconnection Events

```
================================================================================
[DISCONNECT][2025-10-30 22:35:10.789] CLIENT DISCONNECTED - SID: abc123xyz
================================================================================
[DISCONNECT][USER] User 1688 disconnected from SID abc123xyz
```

### 3. Interview Done Emission

#### Successful Emission
```
[FINALIZE][PROCEED] Session 149 finalization starting - first time
[FINALIZE][PRE_EMIT] Session 149, SID abc123xyz, User 1688
[FINALIZE][PRE_EMIT] Active SIDs for user 1688: {'abc123xyz'}
[FINALIZE][EMIT] Sending 'interview done' for session 149
[EMIT][2025-10-30 22:34:47.123] Attempting to emit 'interview done' to user 1688
[EMIT][ACTIVE_SIDS] User 1688 has 1 active SIDs: {'abc123xyz'}
[EMIT][SID_CHECK] SID abc123xyz exists in socketio manager: True
[EMIT][SUCCESS] 'interview done' sent to SID abc123xyz for user 1688
[FINALIZE][EMIT_COMPLETE] 'interview done' emission complete for session 149
```

#### Queued (Client Disconnected)
```
[FINALIZE][PROCEED] Session 149 finalization starting - first time
[FINALIZE][PRE_EMIT] Session 149, SID abc123xyz, User 1688
[FINALIZE][PRE_EMIT] Active SIDs for user 1688: set()
[FINALIZE][EMIT] Sending 'interview done' for session 149
[EMIT][2025-10-30 22:34:47.123] Attempting to emit 'interview done' to user 1688
[EMIT][ACTIVE_SIDS] User 1688 has 0 active SIDs: set()
[EMIT][QUEUE] No active SIDs for user 1688, queuing message 'interview done'
[QUEUE] Queued interview done for user 1688 (queue size: 1)
[FINALIZE][EMIT_COMPLETE] 'interview done' emission complete for session 149
```

#### Duplicate Prevented
```
[FINALIZE][DUPLICATE] Session 149 already finalized. Skipping duplicate finalize.
```

### 4. Message Delivery on Reconnect

```
[DELIVERY][2025-10-30 22:35:16.123] Delivering 3 queued messages to user 1688 via SID xyz789new
[DELIVERY][1/3] Delivering 'interview done' to user 1688
[EMIT][2025-10-30 22:35:16.150] Attempting to emit 'interview done' to user 1688
[EMIT][ACTIVE_SIDS] User 1688 has 1 active SIDs: {'xyz789new'}
[EMIT][SID_CHECK] SID xyz789new exists in socketio manager: True
[EMIT][SUCCESS] 'interview done' sent to SID xyz789new for user 1688
[DELIVERY][SUCCESS] Delivered 'interview done' to user 1688
```

### 5. Dead SID Cleanup

```
[EMIT][SID_CHECK] SID abc123xyz exists in socketio manager: False
[EMIT][CLEANUP] Removed dead SID abc123xyz from user 1688
```

## Troubleshooting Common Issues

### Issue: "interview done" not received by UI

**Look for these patterns in order:**

1. **Was it sent to a live SID?**
   - Check: `[EMIT][SID_CHECK] SID xyz exists in socketio manager: True/False`
   - If `False`: SID was dead, message should have been queued

2. **Was the client still connected when emitted?**
   - Check: `[FINALIZE][PRE_EMIT] Active SIDs for user 1688: {...}`
   - If empty set: client was already disconnected, message was queued

3. **Did the client reconnect with a new SID?**
   - Look for: `[CONNECT][RECONNECTION] User 1688 reconnecting: OLD SID=... -> NEW SID=...`
   - Old SID in emission != New SID = message sent to dead connection

4. **Was the queued message delivered on reconnect?**
   - Check: `[DELIVERY]...[SUCCESS] Delivered 'interview done'`

### Issue: Duplicate "interview done" events

**Look for:**
- Multiple `[FINALIZE][PROCEED]` logs for same session
- Should see `[FINALIZE][DUPLICATE]` on subsequent attempts

If duplicates are still happening:
- Check if `_once_set()` is working properly
- Verify Redis is connected: `[REDIS] Connected to Redis for SID mapping persistence`

### Issue: Premature finalization after reconnect

**Look for:**
- `[FINALIZE][PROCEED]` immediately after `[CONNECT][RECONNECTION]`
- Without corresponding chat completion in DB

Next step: Add DB-backed guard to verify `chat_count >= total_questions` before finalizing.

## Timeline Analysis Example

To trace a full reconnection cycle, grep for the user_id:

```bash
grep "user 1688" socket.log | grep -E "\[CONNECT\]|\[DISCONNECT\]|\[FINALIZE\]|\[EMIT\]|\[DELIVERY\]"
```

Look for the sequence:
1. Initial connection → SID assigned
2. Disconnect (network issue, etc.)
3. Reconnect → new SID assigned → old SID replaced
4. Queued messages delivered to new SID
5. Interview finalization → emit check → success/queue/deliver

## Important Notes

- **Connection timestamps**: Help identify network disruptions
- **SID changes**: Key indicator of reconnection
- **Active SIDs set**: Shows which connections are live for user
- **socketio manager check**: Final validation before actual emit
- **Queue operations**: Fallback when client temporarily unavailable



