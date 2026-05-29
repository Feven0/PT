"""WebSocket middleware."""
from typing import Optional
from fastapi import WebSocket
from ..dependencies import get_session_service
from core.errors import SessionNotFoundError, UnauthorizedError

class WebSocketMiddleware:
    async def authenticate(self, websocket: WebSocket) -> bool:
        """Authenticate WebSocket connection."""
        try:
            # Get authentication token from query parameters or headers
            token = websocket.query_params.get("token") or websocket.headers.get("authorization")
            if not token:
                raise UnauthorizedError("Missing authentication token")

            # Validate token (implement your auth logic here)
            # For example:
            # await auth_service.validate_token(token)
            
            return True
        except Exception as e:
            await websocket.close(code=4001, reason=str(e))
            return False

    async def validate_session(self, websocket: WebSocket, session_id: str) -> bool:
        """Validate session exists and is active."""
        try:
            session_service = get_session_service()
            session = await session_service.get_session(session_id)
            if not session:
                raise SessionNotFoundError(f"Session {session_id} not found")
            
            # Additional session validation logic here
            # For example:
            # if session["status"] != "active":
            #     raise SessionNotFoundError("Session is not active")
            
            return True
        except Exception as e:
            await websocket.close(code=4002, reason=str(e))
            return False

    async def __call__(self, websocket: WebSocket, session_id: str) -> Optional[bool]:
        """Middleware entry point."""
        if not await self.authenticate(websocket):
            return False
            
        if not await self.validate_session(websocket, session_id):
            return False
            
        return True 