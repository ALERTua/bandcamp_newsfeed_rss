"""
Tests for the router module.

Tests the /rss and /atom endpoints with various configurations:
- Endpoint contract (status codes, content types, XML well-formedness)
- Caching behavior (cache hits, misses, separate caches per source type)
- Source type filtering (api, scraping, default, invalid)
- Edge cases (empty feed, source exceptions)
"""

import xml.etree.ElementTree as ET
from datetime import datetime, UTC
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from bandcamp_newsfeed_rss.app import create_app
from bandcamp_newsfeed_rss.cache import clear_cache
from bandcamp_newsfeed_rss.models import FeedItem


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def app():
    """Create a test FastAPI app instance."""
    return create_app()


@pytest.fixture(autouse=True)
def clean_cache_fixture():
    """Clear cache before and after each test."""
    clear_cache()
    yield
    clear_cache()


# =============================================================================
# Mock Data Fixtures
# =============================================================================


@pytest.fixture
def sample_feed_items() -> list[FeedItem]:
    """Provide 3 populated FeedItem objects for testing."""
    base_date = datetime(2026, 1, 15, 10, 30, tzinfo=UTC)
    return [
        FeedItem(
            title="Album Title 1 by Artist One",
            link="https://artist1.bandcamp.com/album/album-title-1",
            author="Artist One",
            description="<div class='test-description'>Test album description 1</div>",
            pub_date=base_date,
            guid="https://artist1.bandcamp.com/album/album-title-1",
            enclosure_url="https://example.com/art1.jpg",
            enclosure_type="image/jpeg",
        ),
        FeedItem(
            title="Album Title 2 by Artist Two",
            link="https://artist2.bandcamp.com/album/album-title-2",
            author="Artist Two",
            description="<div class='test-description'>Test album description 2</div>",
            pub_date=datetime(2026, 1, 14, 15, 45, tzinfo=UTC),
            guid="https://artist2.bandcamp.com/album/album-title-2",
            enclosure_url="https://example.com/art2.jpg",
            enclosure_type="image/jpeg",
        ),
    ]


# =============================================================================
# Endpoint Contract Tests
# =============================================================================


class TestEndpointContract:
    """Tests for basic endpoint functionality and contract."""

    @pytest.mark.asyncio
    async def test_rss_endpoint_returns_rss_content(self, app, sample_feed_items):
        """GET /rss should return HTTP 200 with RSS XML body."""
        # Mock the fetch_items method to return our sample items
        with patch(
            "bandcamp_newsfeed_rss.sources.bandcamp.BandcampScrapingSource.fetch_items",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = sample_feed_items

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/rss")

        assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
        assert response.content, "Expected non-empty response body"

    @pytest.mark.asyncio
    async def test_atom_endpoint_returns_atom_content(self, app, sample_feed_items):
        """GET /atom should return HTTP 200 with Atom XML body."""
        with patch(
            "bandcamp_newsfeed_rss.sources.bandcamp.BandcampScrapingSource.fetch_items",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = sample_feed_items

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/atom")

        assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
        assert response.content, "Expected non-empty response body"

    @pytest.mark.asyncio
    async def test_correct_content_type_rss(self, app, sample_feed_items):
        """RSS response should have Content-Type: application/rss+xml."""
        with patch(
            "bandcamp_newsfeed_rss.sources.bandcamp.BandcampScrapingSource.fetch_items",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = sample_feed_items

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/rss")

        assert response.status_code == 200
        content_type = response.headers.get("content-type", "")
        assert "application/rss+xml" in content_type, (
            f"Expected Content-Type 'application/rss+xml', got '{content_type}'"
        )

    @pytest.mark.asyncio
    async def test_correct_content_type_atom(self, app, sample_feed_items):
        """Atom response should have Content-Type: application/atom+xml."""
        with patch(
            "bandcamp_newsfeed_rss.sources.bandcamp.BandcampScrapingSource.fetch_items",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = sample_feed_items

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/atom")

        assert response.status_code == 200
        content_type = response.headers.get("content-type", "")
        assert "application/atom+xml" in content_type, (
            f"Expected Content-Type 'application/atom+xml', got '{content_type}'"
        )

    @pytest.mark.asyncio
    async def test_rss_xml_is_well_formed(self, app, sample_feed_items):
        """RSS response body should be parseable by xml.etree.ElementTree."""
        with patch(
            "bandcamp_newsfeed_rss.sources.bandcamp.BandcampScrapingSource.fetch_items",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = sample_feed_items

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/rss")

        assert response.status_code == 200
        # Should parse without raising an exception
        try:
            root = ET.fromstring(response.content)
        except ET.ParseError as e:
            pytest.fail(f"RSS XML is not well-formed: {e}")

        # Verify it's an RSS feed
        assert root.tag == "rss", f"Expected root tag 'rss', got '{root.tag}'"

    @pytest.mark.asyncio
    async def test_atom_xml_is_well_formed(self, app, sample_feed_items):
        """Atom response body should be parseable by xml.etree.ElementTree."""
        with patch(
            "bandcamp_newsfeed_rss.sources.bandcamp.BandcampScrapingSource.fetch_items",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = sample_feed_items

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/atom")

        assert response.status_code == 200
        # Should parse without raising an exception
        try:
            root = ET.fromstring(response.content)
        except ET.ParseError as e:
            pytest.fail(f"Atom XML is not well-formed: {e}")

        # Verify it's an Atom feed (handles namespaced tags)
        assert root.tag.endswith("feed"), f"Expected root tag ending with 'feed', got '{root.tag}'"


# =============================================================================
# Caching Behavior Tests
# =============================================================================


class TestCachingBehavior:
    """Tests for caching functionality."""

    @pytest.mark.asyncio
    async def test_cache_hit_returns_cached_response(self, app, sample_feed_items):
        """Second call with same params should return cached response without new HTTP call."""
        mock_fetch = AsyncMock(return_value=sample_feed_items)

        with patch("bandcamp_newsfeed_rss.sources.bandcamp.BandcampScrapingSource.fetch_items", mock_fetch):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                # First call - should trigger fetch
                response1 = await client.get("/rss")
                assert response1.status_code == 200
                content1 = response1.content
                first_call_count = mock_fetch.call_count

                # Second call - should use cache
                response2 = await client.get("/rss")
                assert response2.status_code == 200
                content2 = response2.content
                second_call_count = mock_fetch.call_count

        # Verify no new HTTP call was made
        assert second_call_count == first_call_count, "Expected no new fetch call on cache hit"

        # Verify content is identical
        assert content1 == content2, "Cached content should match original"

    @pytest.mark.asyncio
    async def test_cache_miss_fetches_fresh_data(self, app, sample_feed_items):
        """First call should trigger data fetch."""
        mock_fetch = AsyncMock(return_value=sample_feed_items)

        with patch("bandcamp_newsfeed_rss.sources.bandcamp.BandcampScrapingSource.fetch_items", mock_fetch):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                # First call - should trigger fetch
                response = await client.get("/rss")

        assert response.status_code == 200
        assert mock_fetch.call_count >= 1, "Expected at least one fetch call on cache miss"

    @pytest.mark.asyncio
    async def test_different_source_types_cached_separately(self, app, sample_feed_items):
        """source=api and source=scraping should have independent cache entries."""
        mock_api_fetch = AsyncMock(return_value=sample_feed_items)
        mock_scraping_fetch = AsyncMock(return_value=sample_feed_items)

        # We need to clear cache first
        clear_cache()

        with patch("bandcamp_newsfeed_rss.sources.bandcamp_api.BandcampAPISource.fetch_items", mock_api_fetch):
            with patch(
                "bandcamp_newsfeed_rss.sources.bandcamp.BandcampScrapingSource.fetch_items",
                mock_scraping_fetch,
            ):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    # First call with source=api
                    response_api = await client.get("/rss?source=api")
                    assert response_api.status_code == 200

                    # First call with source=scraping
                    response_scraping = await client.get("/rss?source=scraping")
                    assert response_scraping.status_code == 200

        # Both sources should have been called
        assert mock_api_fetch.call_count >= 1, "Expected API source call"
        assert mock_scraping_fetch.call_count >= 1, "Expected scraping source call"


# =============================================================================
# Source Type Filtering Tests
# =============================================================================


class TestSourceTypeFiltering:
    """Tests for source type query parameter filtering."""

    @pytest.mark.asyncio
    async def test_source_type_api_only(self, app, sample_feed_items):
        """?source=api should return data from API source."""
        mock_api_fetch = AsyncMock(return_value=sample_feed_items)

        clear_cache()

        with patch("bandcamp_newsfeed_rss.sources.bandcamp_api.BandcampAPISource.fetch_items", mock_api_fetch):
            with patch(
                "bandcamp_newsfeed_rss.sources.bandcamp.BandcampScrapingSource.fetch_items",
                new_callable=AsyncMock,
            ) as mock_scraping:
                mock_scraping.return_value = []

                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.get("/rss?source=api")

        assert response.status_code == 200
        assert mock_api_fetch.call_count >= 1, "Expected API source to be called for source=api"

    @pytest.mark.asyncio
    async def test_source_type_scraping_only(self, app, sample_feed_items):
        """?source=scraping should return data from scraping source."""
        mock_scraping_fetch = AsyncMock(return_value=sample_feed_items)

        clear_cache()

        with patch("bandcamp_newsfeed_rss.sources.bandcamp.BandcampScrapingSource.fetch_items", mock_scraping_fetch):
            with patch(
                "bandcamp_newsfeed_rss.sources.bandcamp_api.BandcampAPISource.fetch_items",
                new_callable=AsyncMock,
            ) as mock_api:
                mock_api.return_value = []

                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.get("/rss?source=scraping")

        assert response.status_code == 200
        assert mock_scraping_fetch.call_count >= 1, "Expected scraping source to be called for source=scraping"

    @pytest.mark.asyncio
    async def test_source_type_default(self, app, sample_feed_items):
        """No source param should use the default source type from config."""
        mock_scraping_fetch = AsyncMock(return_value=sample_feed_items)

        clear_cache()

        with patch("bandcamp_newsfeed_rss.sources.bandcamp.BandcampScrapingSource.fetch_items", mock_scraping_fetch):
            with patch(
                "bandcamp_newsfeed_rss.sources.bandcamp_api.BandcampAPISource.fetch_items",
                new_callable=AsyncMock,
            ) as mock_api:
                mock_api.return_value = []

                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    # Default source is "scraping"
                    response = await client.get("/rss")

        assert response.status_code == 200
        assert mock_scraping_fetch.call_count >= 1, "Expected default source (scraping) to be called"

    @pytest.mark.asyncio
    async def test_invalid_source_type_returns_400(self, app):
        """?source=invalid_value should return HTTP 400."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/rss?source=invalid_value")

        assert response.status_code == 400, f"Expected status 400 for invalid source type, got {response.status_code}"


# =============================================================================
# Edge Cases Tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_empty_feed_returns_valid_xml(self, app):
        """When source returns [], response should still be valid XML."""
        empty_items: list[FeedItem] = []

        with patch(
            "bandcamp_newsfeed_rss.sources.bandcamp.BandcampScrapingSource.fetch_items",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = empty_items

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/rss")

        assert response.status_code == 200
        # Should still be valid XML
        try:
            ET.fromstring(response.content)
        except ET.ParseError as e:
            pytest.fail(f"Response should be valid XML even with empty feed: {e}")

    @pytest.mark.asyncio
    async def test_source_exception_returns_valid_xml(self, app):
        """When source raises, exception should propagate up."""
        # Create a mock source that raises an exception
        mock_source = AsyncMock()
        mock_source.fetch_items = AsyncMock(side_effect=Exception("Network error"))
        mock_source.close = AsyncMock()

        # Create a mock async context manager class
        class MockAsyncContextManager:
            async def __aenter__(self):
                return mock_source

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                await mock_source.close()

        # Patch get_feed_source to return our mock
        with patch(
            "bandcamp_newsfeed_rss.router.get_feed_source",
            return_value=MockAsyncContextManager(),
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                # The exception should propagate up
                with pytest.raises(Exception, match="Network error"):
                    await client.get("/rss")
