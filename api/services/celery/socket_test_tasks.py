import asyncio
from api.services.celery.celery_config import celery_app
from api.socket.core import emit_with_log


@celery_app.task(bind=True, name="socket_test_task")
def socket_test_task(self, room: str | None = None, message: str = "hello from celery", sid: str | None = None):
    """Emit a Socket.IO test event from Celery without requiring Redis manager sharing.

    Uses the HTTP client fallback defined in api.socket.core.emit_with_log when the
    Redis manager is not available in this process. Set SOCKETIO_SERVER_URL to the
    FastAPI Socket.IO server URL (e.g., http://localhost:4900 or your public URL).
    """
    payload = {"message": message, "celery_task_id": self.request.id}
    event = "socket_test"
    try:
        print(f"[CELERY] socket_test_task starting id={self.request.id} room={room} msg={message}")
        asyncio.run(emit_with_log(event, payload, room=room, sid=sid))
        print(f"[CELERY] socket_test_task emitted event={event} room={room}")
        return {"status": "ok", "event": event, "room": room}
    except Exception as e:
        print(f"[CELERY] socket_test_task error: {e}")
        return {"status": "error", "error": str(e)}


