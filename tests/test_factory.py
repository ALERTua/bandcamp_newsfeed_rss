"""Tests for the feed source factory."""

import asyncio

import pytest
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException

from bandcamp_newsfeed_rss.models import SourceType
from bandcamp_newsfeed_rss.sources.bandcamp import BandcampScrapingSource
from bandcamp_newsfeed_rss.sources.bandcamp_api import BandcampAPISource
from bandcamp_newsfeed_rss.sources.factory import SOURCE_CLASSES, get_feed_source


# =============================================================================
# Source Creation Tests
# =============================================================================


class TestSourceCreation:
    """Tests for source type creation in the factory."""

    def test_create_api_source(self):
        """Factory with source_type='api' returns instance of BandcampAPISource."""
        # Verify API source type is registered
        assert SourceType.API.value in SOURCE_CLASSES
        assert SOURCE_CLASSES[SourceType.API.value] is BandcampAPISource

    def test_create_scraping_source(self):
        """Factory with source_type='scraping' returns instance of BandcampScrapingSource."""
        # Verify scraping source type is registered
        assert SourceType.SCRAPING.value in SOURCE_CLASSES
        assert SOURCE_CLASSES[SourceType.SCRAPING.value] is BandcampScrapingSource

    def test_invalid_source_type_raises_http_exception(self):
        """Unknown source_type raises HTTPException with status 400."""
        # Attempting to get a source with invalid type should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:  # noqa: PT012

            async def test_invalid():
                async with get_feed_source(source_type="invalid_type"):
                    pass

            # Run the async function - use pytest-asyncio properly
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(test_invalid())
            finally:
                loop.close()

        # Verify the exception status code is 400 (as per actual implementation)
        assert exc_info.value.status_code == 400
        assert "invalid_type" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_source_receives_correct_identity(self):
        """Source instance receives the correct identity token from config."""
        test_token = "test_identity_token_12345"

        with patch("bandcamp_newsfeed_rss.sources.factory.IDENTITY", test_token):
            async with get_feed_source(source_type="api") as source:
                # Verify the source has the correct identity token
                assert source._identity_token == test_token

    @pytest.mark.asyncio
    async def test_source_receives_correct_username(self):
        """Source instance receives the correct username from config."""
        test_username = "testuser"

        with patch("bandcamp_newsfeed_rss.sources.factory.BANDCAMP_USERNAME", test_username):
            async with get_feed_source(source_type="scraping") as source:
                # Verify the source has the correct username
                assert source.bandcamp_username == test_username


# =============================================================================
# Context Manager Lifecycle Tests
# =============================================================================


class TestContextManagerLifecycle:
    """Tests for async context manager lifecycle and cleanup."""

    @pytest.mark.asyncio
    async def test_context_manager_yields_source(self):
        """Async with get_feed_source() yields the source instance."""
        async with get_feed_source(source_type="scraping") as source:
            # Verify we got a BandcampScrapingSource instance
            assert isinstance(source, BandcampScrapingSource)

    @pytest.mark.asyncio
    async def test_context_manager_yields_api_source(self):
        """Async with get_feed_source(source_type='api') yields BandcampAPISource."""
        async with get_feed_source(source_type="api") as source:
            # Verify we got a BandcampAPISource instance
            assert isinstance(source, BandcampAPISource)

    @pytest.mark.asyncio
    async def test_context_manager_cleanup_on_normal_exit(self):
        """Resources cleaned up (client closed) after normal context exit."""
        close_mock = AsyncMock()

        # Patch the close method at class level
        with patch.object(BandcampScrapingSource, "close", close_mock):
            async with get_feed_source(source_type="scraping") as source:
                # Verify source is usable inside context
                assert source is not None
                assert isinstance(source, BandcampScrapingSource)

            # After context exit, close should have been called
            assert close_mock.called, "close() should be called on normal context exit"

    @pytest.mark.asyncio
    async def test_default_source_type_is_scraping(self):
        """Factory defaults to scraping source when no source_type is specified."""
        async with get_feed_source() as source:
            # Default should be scraping source
            assert isinstance(source, BandcampScrapingSource)


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestErrorHandling:
    """Tests for error handling in the factory."""

    def test_invalid_source_type_error_message_contains_available_types(self):
        """HTTPException error message contains available source types."""
        # This is a sync test - test that invalid source type raises correct error
        with pytest.raises(HTTPException) as exc_info:  # noqa: PT012
            # Directly test the factory function behavior
            # The factory will raise before yielding, so we test the exception
            async def test_invalid():
                async with get_feed_source(source_type="unknown"):
                    pass

            # Run using sync wrapper
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(test_invalid())
            finally:
                loop.close()

        error_detail = str(exc_info.value.detail)
        # Should mention available types
        assert "scraping" in error_detail or "api" in error_detail

    @pytest.mark.asyncio
    async def test_empty_string_source_type_raises_error(self):
        """Empty string source_type raises HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            async with get_feed_source(source_type=""):
                pass

        assert exc_info.value.status_code == 400
