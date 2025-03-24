from fastapi import APIRouter

from app.api.routes import documents, users, projects, plugins, estimations, auth

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(plugins.router, prefix="/plugins", tags=["plugins"])
api_router.include_router(estimations.router, prefix="/estimations", tags=["estimations"])
