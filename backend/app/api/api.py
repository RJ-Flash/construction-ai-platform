from fastapi import APIRouter

from .routes import auth, projects, documents, plugins

# Create main API router
api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(plugins.router, prefix="/plugins", tags=["Plugins"])

# Add additional routers as they're created
# api_router.include_router(elements.router, prefix="/elements", tags=["Elements"])
# api_router.include_router(quotes.router, prefix="/quotes", tags=["Quotes"])