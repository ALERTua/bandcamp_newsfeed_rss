"""Unit tests for RSS generator."""

import pytest
from datetime import datetime, UTC

from bandcamp_newsfeed_rss.generators import RSSGenerator
from bandcamp_newsfeed_rss.sources.protocol import FeedItem


class MockFeedSource:
    """Mock feed source for testing."""

    def __init__(self, items: list[FeedItem] | None = None):
        self._url = "https://example.com/feed"
        self._title = "Test Feed"
        self._items = items or [
            FeedItem(
                title="Item 1",
                link="https://example.com/item1",
                author="Author 1",
                description="Description 1",
                pub_date=datetime(2024, 1, 1, tzinfo=UTC),
            ),
        ]

    @property
    def feed_url(self) -> str:
        return self._url

    @property
    def feed_title(self) -> str:
        return self._title

    async def fetch_items(self) -> list[FeedItem]:
        return self._items

    async def close(self) -> None:
        pass


@pytest.mark.asyncio
async def test_generate_rss() -> None:
    """Test RSS generation."""
    source = MockFeedSource()
    generator = RSSGenerator(source)

    result = await generator.generate(atom=False, self_url="https://example.com/rss")

    assert isinstance(result, bytes)
    assert b"<rss" in result
    assert b"Test Feed" in result
    assert b"Item 1" in result


@pytest.mark.asyncio
async def test_generate_atom() -> None:
    """Test Atom generation."""
    source = MockFeedSource()
    generator = RSSGenerator(source)

    result = await generator.generate(atom=True, self_url="https://example.com/atom")

    assert isinstance(result, bytes)
    assert b"<feed" in result
    assert b"Test Feed" in result


@pytest.mark.asyncio
async def test_generate_with_enclosure() -> None:
    """Test RSS generation with enclosure (cover image)."""
    items = [
        FeedItem(
            title="Item with Cover",
            link="https://example.com/item1",
            author="Author",
            description="Description",
            pub_date=datetime.now(UTC),
            enclosure_url="https://example.com/cover.jpg",
            enclosure_type="image/jpeg",
        ),
    ]
    source = MockFeedSource(items=items)
    generator = RSSGenerator(source)

    result = await generator.generate(atom=False)

    assert isinstance(result, bytes)
    assert b"enclosure" in result.lower() or b"<image>" in result.lower()


@pytest.mark.asyncio
async def test_generate_empty_feed() -> None:
    """Test generation with empty feed."""
    source = MockFeedSource(items=[])
    generator = RSSGenerator(source)

    result = await generator.generate(atom=False)

    assert isinstance(result, bytes)
    assert b"<rss" in result
