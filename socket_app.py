from fastapi import FastAPI
from api.socket.core import get_socket_asgi_app


def create_app() -> FastAPI:
    api = FastAPI(title="Socket Test App")
    return api


# Base FastAPI app (for health checks if needed)
_fast = create_app()


@_fast.get("/healthz")
async def healthz():
    return {"status": "ok"}


# Wrap with Socket.IO ASGI app
app = get_socket_asgi_app(_fast)





