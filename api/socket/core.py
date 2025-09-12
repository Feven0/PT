import os
import socketio

# Centralized Socket.IO server instance

_CORS_ORIGINS = os.environ.get("SOCKETIO_CORS_ORIGINS", "*")
_SOCKETIO_PATH = os.environ.get("SOCKETIO_PATH", "/socket.io/")
_ENGINEIO_LOGGER = os.environ.get("SOCKETIO_ENGINEIO_LOGGER", "false").lower() == "true"
_SOCKETIO_LOGGER = os.environ.get("SOCKETIO_LOGGER", "false").lower() == "true"

# Optional: for multi-worker deployments, set REDIS_URL env
_REDIS_URL = os.environ.get("SOCKETIO_REDIS_URL", "")
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


