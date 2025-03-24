"""
API Package

This package contains the API routes for the Construction AI Platform.
"""
from fastapi import APIRouter

# Import all route modules
from app.api.routes import mep

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(mep.router)

__all__ = ["api_router"]
