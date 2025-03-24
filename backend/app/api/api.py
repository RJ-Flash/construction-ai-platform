"""
API router configuration.
"""
from fastapi import APIRouter

from .endpoints import auth, users, projects, document_analysis, quotes

# Main API router
api_router = APIRouter()

# Include all API endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(document_analysis.router, prefix="/documents", tags=["Document Analysis"])
api_router.include_router(quotes.router, prefix="/quotes", tags=["Quotes"])
