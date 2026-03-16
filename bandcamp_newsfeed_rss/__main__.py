import time

from fastapi import FastAPI, status, Response, Request
from pydantic import BaseModel

from .config import (
    CACHE_DURATION_SECONDS,
    BANDCAMP_USERNAME,
    IDENTITY,
    TIMEZONE,
    logger,
)
from .generators import RSSGenerator
from .sources import BandcampScrapingSource

# Cache
cache: dict[str, bytes | None] = {"rss": None, "atom": None}
cache_timestamp: dict[str, float] = {"rss": 0.0, "atom": 0.0}


class FeedSourceManager:
    """Manages cached feed source instance."""

    _instance: BandcampScrapingSource | None = None

    @classmethod
    def get(cls) -> BandcampScrapingSource:
        """Get or create the feed source."""
        if cls._instance is None:
            cls._instance = BandcampScrapingSource(
                username=BANDCAMP_USERNAME,
                identity=IDENTITY,
                timezone=TIMEZONE,
            )
        return cls._instance

    @classmethod
    async def close(cls) -> None:
        """Close the feed source."""
        if cls._instance is not None:
            await cls._instance.close()
            cls._instance = None


async def generate_rss(request: Request, atom: bool = False) -> bytes:  # noqa: FBT001
    """Generate RSS/Atom feed using the modular source."""
    source = FeedSourceManager.get()
    generator = RSSGenerator(source)

    self_url = str(request.url)
    return await generator.generate(atom=atom, self_url=self_url)


async def _rss_feed(request: Request, atom: bool = False):  # noqa: FBT001
    feed_type = "atom" if atom else "rss"
    current_time = time.time()

    # Check cache validity
    if cache.get(feed_type) and (current_time - cache_timestamp.get(feed_type, 0)) < CACHE_DURATION_SECONDS:
        logger.info(f"Returning cached {feed_type} feed")
        return Response(content=cache[feed_type], media_type="application/xml", status_code=status.HTTP_200_OK)

    rss_content = await generate_rss(request, atom=atom)
    cache[feed_type] = rss_content
    cache_timestamp[feed_type] = current_time
    logger.info(f"Generated new {feed_type} feed and updated cache")

    return Response(content=rss_content, media_type="application/xml", status_code=status.HTTP_200_OK)


app = FastAPI()


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: str = "OK"


@app.get("/rss", response_class=Response)
async def rss_feed(request: Request):
    """Endpoint to generate and return the RSS feed."""
    return await _rss_feed(request, atom=False)


@app.get("/atom", response_class=Response)
async def atom_feed(request: Request):
    """Endpoint to generate and return the Atom feed."""
    return await _rss_feed(request, atom=True)


@app.get(
    "/health",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
)
def get_health() -> HealthCheck:
    """Perform a health check."""
    logger.debug("Health check endpoint accessed")
    return HealthCheck(status="OK")


if __name__ == "__main__":
    import os
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        logger.info("Starting up...")
        yield
        await FeedSourceManager.close()
        logger.info("Shutdown complete")

    import uvicorn

    # Recreate app with lifespan for direct run
    app = FastAPI(lifespan=lifespan)

    @app.get("/rss", response_class=Response)
    async def rss_feed(request: Request):
        return await _rss_feed(request, atom=False)

    @app.get("/atom", response_class=Response)
    async def atom_feed(request: Request):
        return await _rss_feed(request, atom=True)

    @app.get("/health", tags=["healthcheck"], status_code=status.HTTP_200_OK)
    def get_health() -> HealthCheck:
        return HealthCheck(status="OK")

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")), log_level="info")
