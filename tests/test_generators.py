"""Unit tests for RSS generator."""

import pytest
from datetime import datetime, UTC

from bandcamp_newsfeed_rss.models import FeedType, FeedItem
from bandcamp_newsfeed_rss.rss import RSSGenerator


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
    generator = RSSGenerator(source, feed_type=FeedType.RSS)

    result = await generator.generate()

    assert isinstance(result, bytes)
    assert b"<rss" in result
    assert b"Test Feed" in result
    assert b"Item 1" in result


@pytest.mark.asyncio
async def test_generate_atom() -> None:
    """Test Atom generation."""
    source = MockFeedSource()
    generator = RSSGenerator(source, feed_type=FeedType.ATOM)

    result = await generator.generate()

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
    generator = RSSGenerator(source, feed_type=FeedType.RSS)

    result = await generator.generate()

    assert isinstance(result, bytes)
    assert b"enclosure" in result.lower() or b"<image>" in result.lower()


@pytest.mark.asyncio
async def test_generate_empty_feed() -> None:
    """Test generation with empty feed."""
    source = MockFeedSource(items=[])
    generator = RSSGenerator(source, feed_type=FeedType.RSS)

    result = await generator.generate()

    assert isinstance(result, bytes)
    assert b"<rss" in result


class MockFailingFeedSource:
    """Mock feed source that raises an exception on fetch_items."""

    def __init__(self, exception_message: str = "Source fetch failed"):
        self._url = "https://example.com/feed"
        self._title = "Test Feed"
        self._exception_message = exception_message

    @property
    def feed_url(self) -> str:
        return self._url

    @property
    def feed_title(self) -> str:
        return self._title

    async def fetch_items(self) -> list[FeedItem]:
        msg = self._exception_message
        raise RuntimeError(msg)

    async def close(self) -> None:
        pass


@pytest.mark.asyncio
async def test_rss_generator_with_source_exception() -> None:
    """Test RSS generator raises exception when source fetch_items raises an exception."""
    source = MockFailingFeedSource(exception_message="Network error")
    generator = RSSGenerator(source, feed_type=FeedType.RSS)

    # The generator propagates the exception from the source
    with pytest.raises(RuntimeError, match="Network error"):
        await generator.generate()


@pytest.mark.asyncio
async def test_atom_generator_with_source_exception() -> None:
    """Test Atom generator raises exception when source fetch_items raises an exception."""
    source = MockFailingFeedSource(exception_message="Network error")
    generator = RSSGenerator(source, feed_type=FeedType.ATOM)

    # The generator propagates the exception from the source
    with pytest.raises(RuntimeError, match="Network error"):
        await generator.generate()


@pytest.mark.asyncio
async def test_rss_generator_with_none_optional_fields() -> None:
    """Test RSS generator handles FeedItem with None for optional fields."""
    # Create a FeedItem with only required fields, None for optional fields
    items = [
        FeedItem(
            title="Item with None fields",
            link="https://example.com/item1",
            author="",  # Empty string instead of None to pass type check
            description="",  # Empty string instead of None to pass type check
            pub_date=datetime(2024, 1, 1, tzinfo=UTC),
            enclosure_url=None,  # Explicitly None
        ),
    ]
    source = MockFeedSource(items=items)
    generator = RSSGenerator(source, feed_type=FeedType.RSS)

    result = await generator.generate()

    assert isinstance(result, bytes)
    assert b"<rss" in result
    assert b"Item with None fields" in result


@pytest.mark.asyncio
async def test_atom_generator_with_none_optional_fields() -> None:
    """Test Atom generator handles FeedItem with None for optional fields."""
    items = [
        FeedItem(
            title="Item with None fields",
            link="https://example.com/item1",
            author="",
            description="",
            pub_date=datetime(2024, 1, 1, tzinfo=UTC),
            enclosure_url=None,
        ),
    ]
    source = MockFeedSource(items=items)
    generator = RSSGenerator(source, feed_type=FeedType.ATOM)

    result = await generator.generate()

    assert isinstance(result, bytes)
    assert b"<feed" in result
    assert b"Item with None fields" in result


@pytest.mark.asyncio
async def test_rss_generator_with_special_characters() -> None:
    """Test RSS generator properly escapes special XML characters in title and description."""
    items = [
        FeedItem(
            title='Test <item> & "test"',
            link="https://example.com/item1",
            author="Author",
            description='Description with <html> & "entities" & more',
            pub_date=datetime(2024, 1, 1, tzinfo=UTC),
        ),
    ]
    source = MockFeedSource(items=items)
    generator = RSSGenerator(source, feed_type=FeedType.RSS)

    result = await generator.generate()

    assert isinstance(result, bytes)
    assert b"<rss" in result
    # Verify special characters are properly escaped
    assert b"&lt;item&gt;" in result or b"<item>" not in result
    assert b"&amp;" in result
    # The XML should be well-formed
    assert result.count(b"<rss") == 1
    assert result.count(b"</rss>") == 1


@pytest.mark.asyncio
async def test_atom_generator_with_special_characters() -> None:
    """Test Atom generator properly escapes special XML characters in title and description."""
    items = [
        FeedItem(
            title='Test <item> & "test"',
            link="https://example.com/item1",
            author="Author",
            description='Description with <html> & "entities" & more',
            pub_date=datetime(2024, 1, 1, tzinfo=UTC),
        ),
    ]
    source = MockFeedSource(items=items)
    generator = RSSGenerator(source, feed_type=FeedType.ATOM)

    result = await generator.generate()

    assert isinstance(result, bytes)
    assert b"<feed" in result
    # Verify special characters are properly escaped
    assert b"&lt;item&gt;" in result or b"<item>" not in result
    assert b"&amp;" in result
    # The XML should be well-formed
    assert result.count(b"<feed") == 1
    assert result.count(b"</feed>") == 1
