from fastapi import APIRouter

from .routes import auth, projects, documents, plugins, subscriptions, users

# Create main API router
api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(plugins.router, prefix="/plugins", tags=["Plugins"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["Subscriptions"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])

# Add additional routers as they're created
# api_router.include_router(elements.router, prefix="/elements", tags=["Elements"])
# api_router.include_router(quotes.router, prefix="/quotes", tags=["Quotes"])