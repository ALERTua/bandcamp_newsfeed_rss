"""Unit tests for feed sources."""

import pytest

from bandcamp_newsfeed_rss.config import BANDCAMP_USERNAME, IDENTITY, TIMEZONE
from bandcamp_newsfeed_rss.rss import RSSGenerator
from bandcamp_newsfeed_rss.models import FeedType, SourceType
from bandcamp_newsfeed_rss.sources import BandcampScrapingSource, BandcampAPISource
from bandcamp_newsfeed_rss.sources.factory import get_feed_source


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_items() -> None:
    """Test fetching items from a feed source."""
    scrap = BandcampScrapingSource(bandcamp_username=BANDCAMP_USERNAME, identity_token=IDENTITY, timezone=TIMEZONE)
    api = BandcampAPISource(bandcamp_username=BANDCAMP_USERNAME, identity_token=IDENTITY, timezone=TIMEZONE)

    scrap_items = await scrap.fetch_items()
    assert len(scrap_items) > 0, "No items found in scraping source"
    scrap_items.sort(key=lambda item: item.pub_date)
    scrap_item = scrap_items[-1]

    api_items = await api.fetch_items()
    assert len(api_items) > 0, "No items found in API source"
    api_items.sort(key=lambda item: item.pub_date)
    api_item = api_items[-1]

    assert scrap_item.title == api_item.title
    assert scrap_item.link == api_item.link


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.parametrize("source_type", SourceType.values())
@pytest.mark.parametrize("feed_type", FeedType.values())
async def test_feed(source_type: str, feed_type: str) -> None:
    """Test generating RSS feed from Bandcamp sources."""
    async with get_feed_source(source_type) as source:
        generator = RSSGenerator(source, feed_type)
        feed = await generator.generate()
        assert len(feed) > 0, f"{source_type.capitalize()} source RSS feed is empty"
        feed_str = feed.decode("utf-8")
        assert "<rss" in feed_str.lower(), f"{source_type.capitalize()} source feed is not valid RSS"
        assert "<channel>" in feed_str.lower(), f"{source_type.capitalize()} source feed missing channel element"
        assert "<item>" in feed_str.lower(), f"{source_type.capitalize()} source feed has no items"

        # Verify tags/categories are included in feed entries if available
        items = await source.fetch_items()
        if items and any(item.tags for item in items):
            assert "<category" in feed_str.lower(), f"{source_type.capitalize()} source feed missing category tags"
