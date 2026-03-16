"""Main entry point for the Bandcamp RSS feed service."""

import os
import time

from fastapi import Request, Response, status
import uvicorn

from .app import create_feed_app
from .config import BANDCAMP_USERNAME, CACHE_DURATION_SECONDS, IDENTITY, TIMEZONE, logger
from .generators import RSSGenerator
from .sources import BandcampScrapingSource


class FeedSourceManager:
    """Manages cached feed source instance."""

    _instance: BandcampScrapingSource | None = None

    @classmethod
    def get(cls) -> BandcampScrapingSource:
        if cls._instance is None:
            cls._instance = BandcampScrapingSource(
                username=BANDCAMP_USERNAME,
                identity=IDENTITY,
                timezone=TIMEZONE,
            )
        return cls._instance

    @classmethod
    async def close(cls) -> None:
        if cls._instance is not None:
            await cls._instance.close()
            cls._instance = None


async def generate_feed(request: Request, atom: bool = False) -> Response:  # noqa: FBT001
    """Generate RSS/Atom feed."""
    feed_type = "atom" if atom else "rss"
    current_time = time.time()

    # Check cache
    if cache.get(feed_type) and (current_time - cache_timestamp.get(feed_type, 0)) < CACHE_DURATION_SECONDS:
        logger.info(f"Returning cached {feed_type} feed")
        return Response(content=cache[feed_type], media_type="application/xml", status_code=status.HTTP_200_OK)

    source = FeedSourceManager.get()
    generator = RSSGenerator(source)
    self_url = str(request.url)

    rss_content = await generator.generate(atom=atom, self_url=self_url)
    cache[feed_type] = rss_content
    cache_timestamp[feed_type] = current_time
    logger.info(f"Generated new {feed_type} feed and updated cache")

    return Response(content=rss_content, media_type="application/xml", status_code=status.HTTP_200_OK)


# Cache
cache: dict[str, bytes | None] = {"rss": None, "atom": None}
cache_timestamp: dict[str, float] = {"rss": 0.0, "atom": 0.0}


def main() -> None:
    app = create_feed_app(generate_feed, FeedSourceManager.close)
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
