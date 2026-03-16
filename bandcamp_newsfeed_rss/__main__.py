import logging
import os
import time
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from fastapi import FastAPI, status, Response, Request
from pydantic import BaseModel

from .generators import RSSGenerator
from .sources import BandcampScrapingSource

load_dotenv()

BANDCAMP_USERNAME = os.getenv("BANDCAMP_USERNAME")
assert BANDCAMP_USERNAME, "BANDCAMP_USERNAME environment variable not set"
IDENTITY = os.getenv("IDENTITY")
assert IDENTITY, "IDENTITY environment variable not set"

VERBOSE = os.getenv("VERBOSE", "0")
log_level = logging.DEBUG if VERBOSE == "1" else logging.INFO

logging.basicConfig(
    level=log_level,
    format="%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)
logger.info(f"Logging level set to {'DEBUG' if log_level == logging.DEBUG else 'INFO'}")

# Cache configuration
CACHE_DURATION_SECONDS = int(os.getenv("CACHE_DURATION_SECONDS", "3600"))
cache: dict[str, bytes | None] = {"rss": None, "atom": None}
cache_timestamp: dict[str, float] = {"rss": 0.0, "atom": 0.0}

TZ = os.getenv("TZ", "Europe/London")
TIMEZONE = ZoneInfo(TZ)

app = FastAPI()


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: str = "OK"


def get_feed_source() -> BandcampScrapingSource:
    """Create and return the Bandcamp feed source."""
    return BandcampScrapingSource(
        username=BANDCAMP_USERNAME,
        identity=IDENTITY,
        timezone=TIMEZONE,
    )


def generate_rss(request: Request, atom: bool = False) -> bytes:  # noqa: FBT001
    """Generate RSS/Atom feed using the modular source."""
    source = get_feed_source()
    generator = RSSGenerator(source)

    self_url = str(request.url)
    return generator.generate(atom=atom, self_url=self_url)


async def _rss_feed(request: Request, atom: bool = False):  # noqa: FBT001
    feed_type = "atom" if atom else "rss"
    current_time = time.time()

    # Check cache validity
    if cache.get(feed_type) and (current_time - cache_timestamp.get(feed_type, 0)) < CACHE_DURATION_SECONDS:
        logger.info(f"Returning cached {feed_type} feed")
        return Response(content=cache[feed_type], media_type="application/xml", status_code=status.HTTP_200_OK)

    rss_content = generate_rss(request, atom=atom)
    cache[feed_type] = rss_content
    cache_timestamp[feed_type] = current_time
    logger.info(f"Generated new {feed_type} feed and updated cache")

    return Response(content=rss_content, media_type="application/xml", status_code=status.HTTP_200_OK)


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
    """
    ## Perform a Health Check
    Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
    to ensure a robust container orchestration and management is in place. Other
    services which rely on proper functioning of the API service will not deploy if this
    endpoint returns any other HTTP status code except 200 (OK).

    Returns
    -------
        HealthCheck: Returns a JSON response with the health status

    """
    logger.debug("Health check endpoint accessed")
    return HealthCheck(status="OK")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")), log_level="info")
