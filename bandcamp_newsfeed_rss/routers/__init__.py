"""Feed routers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Request, Response, status

from bandcamp_newsfeed_rss.cache import get_cached, set_cached
from bandcamp_newsfeed_rss.config import logger
from bandcamp_newsfeed_rss.generators import RSSGenerator

if TYPE_CHECKING:
    from bandcamp_newsfeed_rss.sources import BandcampScrapingSource


def create_feed_router(
    source_class: type[BandcampScrapingSource],
    prefix: str = "",
) -> APIRouter:
    """
    Create a feed router for a given source class.

    Args:
        source_class: The feed source class to use
        prefix: URL prefix for the router (e.g., "/personal")

    Returns:
        Configured APIRouter with /rss and /atom endpoints

    """
    router = APIRouter(prefix=prefix)

    async def generate_feed(request: Request, atom: bool = False) -> Response:  # noqa: FBT001
        """Generate RSS/Atom feed."""
        feed_type = "atom" if atom else "rss"

        # Check cache
        cached = get_cached(feed_type)
        if cached:
            return Response(
                content=cached,
                media_type="application/atom+xml" if atom else "application/rss+xml",
                status_code=status.HTTP_200_OK,
            )

        source = source_class()
        generator = RSSGenerator(source)
        self_url = str(request.url)

        rss_content = await generator.generate(atom=atom, self_url=self_url)
        set_cached(feed_type, rss_content)

        return Response(
            content=rss_content,
            media_type="application/atom+xml" if atom else "application/rss+xml",
            status_code=status.HTTP_200_OK,
        )

    @router.get("/rss")
    async def rss(request: Request):
        """RSS feed endpoint."""
        return await generate_feed(request, atom=False)

    @router.get("/atom")
    async def atom(request: Request):
        """Atom feed endpoint."""
        return await generate_feed(request, atom=True)

    return router
