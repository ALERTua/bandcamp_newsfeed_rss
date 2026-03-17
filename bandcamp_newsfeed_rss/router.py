from typing import Annotated

from fastapi import APIRouter, Query
from starlette import status
from starlette.responses import Response

from .cache import get_cached, set_cached
from .rss import RSSGenerator
from .models import SourceType, FeedType
from .sources.factory import get_feed_source


SOURCE_TYPES = SourceType.values()
DEFAULT_SOURCE_TYPE = SourceType.SCRAPING.value


def create_router() -> APIRouter:
    """
    Create a feed router using the factory dependency.

    Returns:
        Configured APIRouter with /rss and /atom endpoints

    """
    router = APIRouter()

    async def generate_feed(
        feed_type: str = FeedType.RSS,
        source: Annotated[str, Query(description=f"Source type: {SOURCE_TYPES}")] = DEFAULT_SOURCE_TYPE,
    ) -> Response:
        """Generate RSS feed."""
        cache_key = f"{feed_type}:{source}"
        media_type = "application/atom+xml" if feed_type == FeedType.ATOM else "application/rss+xml"

        cached = get_cached(cache_key)
        if cached:
            return Response(
                content=cached,
                media_type=media_type,
                status_code=status.HTTP_200_OK,
            )

        async with get_feed_source(source) as feed_source:
            generator = RSSGenerator(feed_source, feed_type=feed_type)
            rss_content = await generator.generate()

        set_cached(cache_key, rss_content)

        return Response(
            content=rss_content,
            media_type=media_type,
            status_code=status.HTTP_200_OK,
        )

    @router.get("/rss")
    async def rss(
        source: Annotated[str, Query(description=f"Source type: {SOURCE_TYPES}")] = DEFAULT_SOURCE_TYPE,
    ):
        """RSS feed endpoint."""
        return await generate_feed(source=source, feed_type=FeedType.RSS)

    @router.get("/atom")
    async def atom(
        source: Annotated[str, Query(description=f"Source type: {SOURCE_TYPES}")] = DEFAULT_SOURCE_TYPE,
    ):
        """Atom feed endpoint."""
        return await generate_feed(source=source, feed_type=FeedType.ATOM)

    return router
