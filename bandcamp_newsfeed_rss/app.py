"""FastAPI application factory."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from .models import HealthCheck
from .config import logger


def create_feed_app(feed_generator_func, shutdown_func) -> FastAPI:
    """
    Create FastAPI app with feed endpoints.

    Args:
        feed_generator_func: Async function that generates RSS/Atom feed
        shutdown_func: Async function to call on shutdown

    """

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        logger.info("Starting up...")
        yield
        await shutdown_func()
        logger.info("Shutdown complete")

    app = FastAPI(lifespan=lifespan)

    @app.get("/rss")
    async def rss_feed(request: Request):
        return await feed_generator_func(request, atom=False)

    @app.get("/atom")
    async def atom_feed(request: Request):
        return await feed_generator_func(request, atom=True)

    @app.get("/health", tags=["healthcheck"])
    def health() -> HealthCheck:
        return HealthCheck(status="OK")

    return app
