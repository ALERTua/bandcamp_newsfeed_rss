"""Unit tests for feed sources."""

import pytest
from datetime import datetime, UTC

from bandcamp_newsfeed_rss.models import FeedItem
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bandcamp_newsfeed_rss.sources.protocol import FeedSource


class MockFeedSource:
    """Mock feed source for testing."""

    def __init__(self):
        self._url = "https://example.com/feed"
        self._title = "Mock Feed"

    @property
    def feed_url(self) -> str:
        return self._url

    @property
    def feed_title(self) -> str:
        return self._title

    async def fetch_items(self) -> list[FeedItem]:
        return [
            FeedItem(
                title="Test Item",
                link="https://example.com/item1",
                author="Test Author",
                description="Test description",
                pub_date=datetime.now(UTC),
            ),
        ]

    async def close(self) -> None:
        pass


def test_feed_source_protocol() -> None:
    """Test that MockFeedSource implements FeedSource protocol."""
    source: FeedSource = MockFeedSource()
    assert source.feed_url == "https://example.com/feed"
    assert source.feed_title == "Mock Feed"


@pytest.mark.asyncio
async def test_fetch_items() -> None:
    """Test fetching items from a feed source."""
    source = MockFeedSource()
    items = await source.fetch_items()

    assert len(items) == 1
    assert items[0].title == "Test Item"
    assert items[0].author == "Test Author"


def test_feed_item_creation() -> None:
    """Test FeedItem creation with all fields."""
    item = FeedItem(
        title="Title",
        link="https://example.com",
        author="Author",
        description="Description",
        pub_date=datetime.now(UTC),
        guid="guid-123",
        enclosure_url="https://example.com/cover.jpg",
    )

    assert item.title == "Title"
    assert item.link == "https://example.com"
    assert item.author == "Author"
    assert item.guid == "guid-123"
    assert item.enclosure_url == "https://example.com/cover.jpg"
