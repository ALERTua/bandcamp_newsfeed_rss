"""FastAPI application factory."""

from fastapi import FastAPI

from .models import HealthCheck
from .router import create_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI()

    router = create_router()
    app.include_router(router)

    @app.get("/health", tags=["healthcheck"])
    def health() -> HealthCheck:
        return HealthCheck(status="OK")

    return app
