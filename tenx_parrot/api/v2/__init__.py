"""API v2 routes."""
from fastapi import APIRouter
from .routes.analysis import router as analysis_router
from .routes.interview import router as interview_router
from .routes.prompts import router as prompts_router
from .routes.session import router as session_router


router = APIRouter(prefix="/v2")

# Include all route modules
router.include_router(analysis_router)
router.include_router(interview_router)
router.include_router(prompts_router)
router.include_router(session_router)
