"""Unit tests for source registry."""

from bandcamp_newsfeed_rss.sources.registry import (
    FEED_SOURCES,
    get_source_class,
    register_source,
)
from bandcamp_newsfeed_rss.sources.protocol import FeedSource


class MockSourceA(FeedSource):
    """Mock source A for testing."""

    @property
    def feed_url(self) -> str:
        return "https://a.example.com"

    @property
    def feed_title(self) -> str:
        return "Source A"

    async def fetch_items(self):
        return []

    async def close(self):
        pass


class MockSourceB(FeedSource):
    """Mock source B for testing."""

    @property
    def feed_url(self) -> str:
        return "https://b.example.com"

    @property
    def feed_title(self) -> str:
        return "Source B"

    async def fetch_items(self):
        return []

    async def close(self):
        pass


def test_register_source() -> None:
    """Test registering a new source."""
    initial_count = len(FEED_SOURCES)

    @register_source("test_source")
    class TestSource(FeedSource):
        @property
        def feed_url(self) -> str:
            return "https://test.com"

        @property
        def feed_title(self) -> str:
            return "Test"

        async def fetch_items(self):
            return []

        async def close(self):
            pass

    assert "test_source" in FEED_SOURCES
    assert len(FEED_SOURCES) == initial_count + 1


def test_get_source_class_existing() -> None:
    """Test getting an existing source class."""
    result = get_source_class("scraping")
    assert result is not None


def test_get_source_class_nonexisting() -> None:
    """Test getting a non-existing source class."""
    result = get_source_class("nonexistent_source_xyz")
    assert result is None


def test_scraping_source_registered() -> None:
    """Test that scraping source is registered."""
    assert "scraping" in FEED_SOURCES
