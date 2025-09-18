import os
import asyncio
import socketio

# Centralized Socket.IO server instance

_CORS_ORIGINS = os.environ.get("SOCKETIO_CORS_ORIGINS", "*")
_SOCKETIO_PATH = os.environ.get("SOCKETIO_PATH", "/socket.io/")
_ENGINEIO_LOGGER = os.environ.get("SOCKETIO_ENGINEIO_LOGGER", "false").lower() == "true"
_SOCKETIO_LOGGER = os.environ.get("SOCKETIO_LOGGER", "false").lower() == "true"

# Optional: for multi-worker deployments, set REDIS_URL env
# Resolve Redis URL with credentials from env or config
_ENV_REDIS_URL = os.environ.get("SOCKETIO_REDIS_URL", "")
if not _ENV_REDIS_URL:
    try:
        # api/config.py defines REDIS_URL like: redis://:PASSWORD@HOST:PORT
        from api import config as _cfg
        _BASE_REDIS_URL = getattr(_cfg, "REDIS_URL", "")
    except Exception:
        _BASE_REDIS_URL = ""
    # Ensure a DB index is present (default to /0)
    if _BASE_REDIS_URL and not _BASE_REDIS_URL.rstrip().split("/")[-1].isdigit():
        _REDIS_URL = _BASE_REDIS_URL + "/0"
    else:
        _REDIS_URL = _BASE_REDIS_URL or ""
else:
    _REDIS_URL = _ENV_REDIS_URL
_CLIENT_MANAGER = None
if _REDIS_URL:
    try:
        from socketio import AsyncRedisManager
        _CLIENT_MANAGER = AsyncRedisManager(_REDIS_URL)
    except Exception:
        _CLIENT_MANAGER = None

sio = socketio.AsyncServer(
    cors_allowed_origins=_CORS_ORIGINS,
    async_mode="asgi",
    logger=_SOCKETIO_LOGGER,
    engineio_logger=_ENGINEIO_LOGGER,
    client_manager=_CLIENT_MANAGER,
)

def get_socket_asgi_app(fast_app):
    return socketio.ASGIApp(
        socketio_server=sio,
        other_asgi_app=fast_app,
        socketio_path=_SOCKETIO_PATH,
    )

async def emit_to_job(job_id: str, event: str, data):
    room = f"processing_{job_id}"
    await sio.emit(event, data, room=room)

# Debug helper to log emits from any process (API or Celery)
async def emit_with_log(event: str, data: dict, room: str | None = None):
    try:
        ns = "/"
        approx_targets = "unknown"
        try:
            if room:
                participants = await sio.get_participants(ns, room)
                approx_targets = len(participants) if participants is not None else 0
            else:
                # engineio has no direct count; rely on sessions when available
                approx_targets = "broadcast"
        except Exception:
            pass
        print(f"[SIO] → Emitting event='{event}' room='{room or 'ALL'}' targets≈{approx_targets} keys={list(data.keys())}")
        try:
            await sio.emit(event, data, room=room)
            print(f"[SIO] ✓ Emitted event='{event}' via manager")
            return
        except Exception as e:
            print("Cannot publish to redis... retrying")
            print(f"[SIO] manager emit failed: {e}")
            # Fallback: emit via transient Socket.IO client to the server URL
            await _emit_via_client(event, data)
            print(f"[SIO] ✓ Emitted event='{event}' via client fallback")
    except Exception as e:
        print(f"[SIO] ✗ Emit failed event='{event}': {e}")

async def _emit_via_client(event: str, data: dict):
    try:
        import socketio as _sio
        server_url = os.environ.get("SOCKETIO_SERVER_URL") or os.environ.get("WS_PUBLIC_URL") or "http://localhost:9900"
        client = _sio.AsyncClient()
        # Prefer websocket to avoid long-poll fallback issues
        await client.connect(server_url, transports=['websocket'])
        await client.emit(event, data)
        await client.disconnect()
    except Exception as e:
        print(f"[SIO] client fallback failed: {e}")

async def emit_to_user_job(job_id: str, user_id: str, event: str, data):
    """Emit to user-specific job room"""
    room = f"processing_{job_id}_{user_id}"
    await sio.emit(event, data, room=room)

async def websocket_notification_callback(notification):
    """Handle Redis notifications and emit to appropriate WebSocket rooms"""
    try:
        notification_type = notification.get('type')
        
        if notification_type == 's3_upload_complete':
            job_id = notification.get('job_id')
            user_id = notification.get('user_id')
            
            # Handle None/null job_id (common in Celery tasks)
            if job_id is None:
                job_id = "None"
            
            if user_id and (job_id or job_id == "None"):
                await emit_to_user_job(job_id, user_id, 's3_upload_complete', notification)
                print(f"📡 [DEBUG] Emitted S3 completion to room processing_{job_id}_{user_id}")
            else:
                print(f"❌ [DEBUG] Missing job_id or user_id in S3 notification: {notification}")
        else:
            # Handle other notification types
            print(f"📡 [DEBUG] Unhandled notification type: {notification_type}")
            
    except Exception as e:
        print(f"❌ [DEBUG] Error in websocket_notification_callback: {str(e)}")

async def join_job_room(sid: str, job_id: str):
    await sio.enter_room(sid, f"processing_{job_id}")

async def leave_job_room(sid: str, job_id: str):
    await sio.leave_room(sid, f"processing_{job_id}")

def get_room_members(job_id: str):
    try:
        namespace_rooms = getattr(sio.manager, 'rooms', {}).get('/', {})
        return list(namespace_rooms.get(f"processing_{job_id}", set()))
    except Exception:
        return []

def get_processing_rooms():
    try:
        namespace_rooms = getattr(sio.manager, 'rooms', {}).get('/', {})
        return {r: list(s) for r, s in namespace_rooms.items() if isinstance(r, str) and r.startswith('processing_')}
    except Exception:
        return {}


