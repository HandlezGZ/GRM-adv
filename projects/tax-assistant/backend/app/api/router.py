from fastapi import APIRouter

from backend.app.api.routes.chat import router as chat_router
from backend.app.api.routes.dashboard import router as dashboard_router
from backend.app.api.routes.documents import router as documents_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(documents_router)
api_v1_router.include_router(chat_router)
api_v1_router.include_router(dashboard_router)
