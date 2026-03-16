"""FastAPI application factory."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .models import HealthCheck
from .routers import create_feed_router
from .sources import BandcampScrapingSource
from .config import logger, BANDCAMP_USERNAME, IDENTITY, TIMEZONE


def create_feed_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Create source instance at module level
    scraping_source = BandcampScrapingSource(
        username=BANDCAMP_USERNAME,
        identity=IDENTITY,
        timezone=TIMEZONE,
    )

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        logger.info("Starting up...")
        yield
        # Cleanup: close source connections on shutdown
        await scraping_source.close()
        logger.info("Shutdown complete")

    app = FastAPI(lifespan=lifespan)

    # Include feed routers
    scraping_router = create_feed_router(scraping_source, prefix="")
    app.include_router(scraping_router)

    @app.get("/health", tags=["healthcheck"])
    def health() -> HealthCheck:
        return HealthCheck(status="OK")

    return app
