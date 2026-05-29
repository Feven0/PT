# WebRTC Service

The WebRTC service provides real-time communication capabilities for audio/video streaming and data channels in the backend system. It implements a complete WebRTC signaling server with support for ICE candidates, offers/answers, and WebSocket-based signaling.

## Features

- WebSocket-based signaling server
- ICE candidate exchange
- SDP offer/answer negotiation
- Connection state management
- Configurable STUN/TURN servers
- Metrics collection
- Lifecycle management
- Redis-based state caching

## Usage

### Basic Setup

```python
from core.cache.manager import CacheManager
from core.telemetry.metrics import MetricsCollector
from services.webrtc import WebRTCService

# Create dependencies
cache = CacheManager()
metrics = MetricsCollector()

# Create WebRTC service
webrtc = WebRTCService(
    cache=cache,
    metrics=metrics,
    stun_servers={"stun:stun.l.google.com:19302"},
    turn_servers=set(),  # Add TURN servers if needed
    ice_transport_policy="all",
    bundle_policy="balanced"
)

# Initialize and start
await webrtc.initialize()
await webrtc.start()
```

### Handling WebRTC Signaling

```python
# In your FastAPI route
@router.websocket("/signaling/{session_id}")
async def webrtc_signaling(websocket: WebSocket, session_id: str):
    await webrtc.handle_signaling(websocket, session_id)
```

### Creating Offers

```python
# Create an offer with custom config
config = {
    "offerToReceiveAudio": True,
    "offerToReceiveVideo": True
}
offer = await webrtc.create_offer(session_id, config)
```

### Handling Answers

```python
# Handle an answer from the peer
answer = {
    "type": "answer",
    "sdp": "v=0\r\n..."
}
result = await webrtc.handle_answer(session_id, answer)
```

### ICE Candidates

```python
# Handle an ICE candidate
candidate = {
    "candidate": "candidate:1 1 UDP 2122260223 192.168.1.1 54321 typ host",
    "sdpMLineIndex": 0,
    "sdpMid": "0"
}
result = await webrtc.handle_ice_candidate(session_id, candidate)
```

### Connection Status

```python
# Get connection status
status = await webrtc.get_connection_status(session_id)
if status:
    print(f"Active: {status['active']}")
    print(f"Config: {status['config']}")
```

## Advanced Features

### Custom STUN/TURN Servers

```python
webrtc = WebRTCService(
    cache=cache,
    metrics=metrics,
    stun_servers={
        "stun:stun1.l.google.com:19302",
        "stun:stun2.l.google.com:19302"
    },
    turn_servers={
        "turn:turn.example.com:3478?transport=udp",
        "turn:turn.example.com:3478?transport=tcp"
    }
)
```

### ICE Transport Policy

```python
# Force relay-only ICE candidates
webrtc = WebRTCService(
    cache=cache,
    metrics=metrics,
    ice_transport_policy="relay"
)
```

### Bundle Policy

```python
# Set max-bundle policy
webrtc = WebRTCService(
    cache=cache,
    metrics=metrics,
    bundle_policy="max-bundle"
)
```

## Metrics

The service collects the following metrics:

- `webrtc_connection_opened`: Counter for new WebSocket connections
- `webrtc_connection_closed`: Counter for closed WebSocket connections
- `webrtc_connection_error`: Counter for WebSocket errors
- `webrtc_message_handled`: Counter for handled WebRTC messages
- `webrtc_offer_created`: Counter for created offers
- `webrtc_offer_error`: Counter for offer creation errors
- `webrtc_answer_handled`: Counter for handled answers
- `webrtc_answer_error`: Counter for answer handling errors
- `webrtc_ice_handled`: Counter for handled ICE candidates
- `webrtc_ice_error`: Counter for ICE candidate handling errors

## Lifecycle Management

The service implements the `LifecycleAware` protocol and manages its state through the following lifecycle:

1. `UNINITIALIZED`: Initial state
2. `INITIALIZED`: After `initialize()` is called
3. `RUNNING`: After `start()` is called
4. `STOPPING`: During shutdown
5. `STOPPED`: After cleanup

## Error Handling

The service includes comprehensive error handling:

- State validation before operations
- Connection management
- WebSocket error handling
- Metrics for all error cases
- Graceful connection cleanup

## Dependencies

- FastAPI for WebSocket support
- Redis for state caching
- Prometheus client for metrics
- Core lifecycle management

## Best Practices

1. Always initialize and start the service before use
2. Handle WebSocket disconnections gracefully
3. Monitor metrics for errors and performance
4. Use appropriate STUN/TURN servers for production
5. Implement proper security measures
6. Clean up resources on shutdown

## Security Considerations

1. Use secure WebSocket connections (wss://)
2. Implement authentication for signaling
3. Use TURN servers with proper credentials
4. Monitor for suspicious connection patterns
5. Rate limit signaling endpoints
6. Validate all incoming messages 