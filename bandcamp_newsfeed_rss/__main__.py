"""Main entry point for the Bandcamp RSS feed service."""

import os

from fastapi import Request, Response, status
import uvicorn

from .app import create_feed_app
from .cache import get_cached, set_cached
from .config import BANDCAMP_USERNAME, IDENTITY, TIMEZONE
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

    # Check cache
    cached = get_cached(feed_type)
    if cached:
        return Response(content=cached, media_type=get_media_type(atom), status_code=status.HTTP_200_OK)

    source = FeedSourceManager.get()
    generator = RSSGenerator(source)
    self_url = str(request.url)

    rss_content = await generator.generate(atom=atom, self_url=self_url)
    set_cached(feed_type, rss_content)

    return Response(content=rss_content, media_type=get_media_type(atom), status_code=status.HTTP_200_OK)


def get_media_type(atom: bool) -> str:  # noqa: FBT001
    """Get correct media type for feed."""
    return "application/atom+xml" if atom else "application/rss+xml"


def main() -> None:
    app = create_feed_app(generate_feed, FeedSourceManager.close)
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
