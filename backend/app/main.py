from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.api import itinerary, expense, navigation, voice


# Initialize logging before creating the application instance.
setup_logging()
logger = get_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered travel planning platform with itinerary generation and expense tracking",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(itinerary.router, prefix="/api")
app.include_router(expense.router, prefix="/api")
app.include_router(navigation.router, prefix="/api")
app.include_router(voice.router, prefix="/api")


@app.on_event("startup")
async def on_startup() -> None:
    """Log successful startup."""
    logger.info("%s v%s is starting up", settings.APP_NAME, settings.APP_VERSION)


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """Log graceful shutdown."""
    logger.info("%s is shutting down", settings.APP_NAME)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to AI Travel Planner API",
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG
    )
