"""FastAPI application factory."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any
from collections.abc import Callable

from fastapi import FastAPI

from .models import HealthCheck
from .config import logger

if TYPE_CHECKING:
    from collections.abc import Callable


def create_feed_app(
    feed_generator_func: Callable[..., Any],
    shutdown_func: Callable[..., Any],
) -> FastAPI:
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
    async def rss_feed(request: Any) -> Any:
        return await feed_generator_func(request, atom=False)

    @app.get("/atom")
    async def atom_feed(request: Any) -> Any:
        return await feed_generator_func(request, atom=True)

    @app.get("/health", tags=["healthcheck"])
    def health() -> HealthCheck:
        return HealthCheck(status="OK")

    return app
