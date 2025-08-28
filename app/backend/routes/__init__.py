from fastapi import APIRouter

from app.backend.routes.health import router as health_router
from app.backend.routes.projects import router as projects_router
from app.backend.routes.contacts import router as contacts_router
from app.backend.routes.companies import router as companies_router
from app.backend.routes.signals import router as signals_router
from app.backend.routes.tasks import router as tasks_router
from app.backend.routes.upload import router as upload_router
from app.backend.routes.dashboard import router as dashboard_router

# Main API router
api_router = APIRouter(prefix="/api/v1")

# Include sub-routers
api_router.include_router(health_router, tags=["health"])
api_router.include_router(projects_router, tags=["projects"])
api_router.include_router(contacts_router, tags=["contacts"])
api_router.include_router(companies_router, tags=["companies"])
api_router.include_router(signals_router, tags=["signals"])
api_router.include_router(tasks_router, tags=["tasks"])
api_router.include_router(upload_router, tags=["upload"])
api_router.include_router(dashboard_router, tags=["dashboard"])
