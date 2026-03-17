"""Unit tests for feed sources."""

import pytest

from bandcamp_newsfeed_rss.sources import BandcampScrapingSource, BandcampAPISource
from bandcamp_newsfeed_rss.config import IDENTITY, BANDCAMP_USERNAME, TIMEZONE


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_rss() -> None:
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
