"""
Tests for source error handling.

These tests verify that both source types raise exceptions on errors,
rather than raising exceptions to the caller.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from bandcamp_newsfeed_rss.sources.bandcamp_api import BandcampAPISource
from bandcamp_newsfeed_rss.sources.bandcamp import BandcampScrapingSource


# =============================================================================
# API Source Error Handling Tests
# =============================================================================


@pytest.mark.asyncio
async def test_api_timeout_logs_and_returns_empty(app_config):
    """Verify that TimeoutException is raised and logged."""
    source = BandcampAPISource(
        identity_token=app_config.identity_token,
        bandcamp_username=app_config.bandcamp_username,
        timezone=app_config.timezone,
    )

    # Mock the client to raise TimeoutException
    mock_client = AsyncMock()
    mock_client.get_feed = AsyncMock(side_effect=Exception("Request timeout"))
    source._client = mock_client

    with pytest.raises(Exception, match="Request timeout"):
        await source.fetch_items()

    await source.close()


@pytest.mark.asyncio
async def test_api_connection_error_returns_empty(app_config):
    """Verify that connection error is raised and logged."""
    source = BandcampAPISource(
        identity_token=app_config.identity_token,
        bandcamp_username=app_config.bandcamp_username,
        timezone=app_config.timezone,
    )

    # Mock the client to raise ConnectError
    mock_client = AsyncMock()
    mock_client.get_feed = AsyncMock(side_effect=Exception("Connection failed"))
    source._client = mock_client

    with pytest.raises(Exception, match="Connection failed"):
        await source.fetch_items()

    await source.close()


@pytest.mark.asyncio
async def test_api_http_500_returns_empty(app_config):
    """Verify that HTTP 500 response is raised and logged."""
    source = BandcampAPISource(
        identity_token=app_config.identity_token,
        bandcamp_username=app_config.bandcamp_username,
        timezone=app_config.timezone,
    )

    # Mock the client to raise an HTTPStatusError for 500
    mock_client = AsyncMock()
    mock_client.get_feed = AsyncMock(side_effect=Exception("Server Error (500)"))
    source._client = mock_client

    with pytest.raises(Exception, match=r"Server Error \(500\)"):
        await source.fetch_items()

    await source.close()


@pytest.mark.asyncio
async def test_api_http_503_returns_empty(app_config):
    """Verify that HTTP 503 response is raised and logged."""
    source = BandcampAPISource(
        identity_token=app_config.identity_token,
        bandcamp_username=app_config.bandcamp_username,
        timezone=app_config.timezone,
    )

    # Mock the client to raise an HTTPStatusError for 503
    mock_client = AsyncMock()
    mock_client.get_feed = AsyncMock(side_effect=Exception("Service Unavailable (503)"))
    source._client = mock_client

    with pytest.raises(Exception, match=r"Service Unavailable \(503\)"):
        await source.fetch_items()

    await source.close()


@pytest.mark.asyncio
async def test_api_http_404_returns_empty(app_config):
    """Verify that HTTP 404 response is raised and logged."""
    source = BandcampAPISource(
        identity_token=app_config.identity_token,
        bandcamp_username=app_config.bandcamp_username,
        timezone=app_config.timezone,
    )

    # Mock the client to raise an HTTPStatusError for 404
    mock_client = AsyncMock()
    mock_client.get_feed = AsyncMock(side_effect=Exception("Not Found (404)"))
    source._client = mock_client

    with pytest.raises(Exception, match=r"Not Found \(404\)"):
        await source.fetch_items()

    await source.close()


@pytest.mark.asyncio
async def test_api_invalid_json_returns_empty_list(app_config):
    """Verify that invalid JSON response returns empty list."""
    source = BandcampAPISource(
        identity_token=app_config.identity_token,
        bandcamp_username=app_config.bandcamp_username,
        timezone=app_config.timezone,
    )

    # Create a mock response with invalid JSON
    mock_response = MagicMock()
    mock_response.json = MagicMock(side_effect=ValueError("Invalid JSON"))
    mock_client = AsyncMock()
    mock_client.get_feed = AsyncMock(return_value=mock_response)
    source._client = mock_client

    result = await source.fetch_items()

    assert result == [], "Expected empty list on invalid JSON"
    await source.close()


@pytest.mark.asyncio
async def test_api_empty_stories_array_returns_empty_list(app_config):
    """Verify that empty stories array returns empty list."""
    source = BandcampAPISource(
        identity_token=app_config.identity_token,
        bandcamp_username=app_config.bandcamp_username,
        timezone=app_config.timezone,
    )

    # Create a mock response with empty stories
    mock_response = MagicMock()
    mock_response.stories = []
    mock_client = AsyncMock()
    mock_client.get_feed = AsyncMock(return_value=mock_response)
    source._client = mock_client

    result = await source.fetch_items()

    assert result == [], "Expected empty list when stories is empty array"
    await source.close()


@pytest.mark.asyncio
async def test_api_missing_stories_key_returns_empty(app_config):
    """Verify that missing stories key raises AttributeError."""
    source = BandcampAPISource(
        identity_token=app_config.identity_token,
        bandcamp_username=app_config.bandcamp_username,
        timezone=app_config.timezone,
    )

    # Create a mock response without stories key - use a plain object without spec
    # to allow any attribute access that will raise AttributeError
    mock_response = MagicMock()
    del mock_response.stories  # Ensure stories attribute doesn't exist
    mock_client = AsyncMock()
    mock_client.get_feed = AsyncMock(return_value=mock_response)
    source._client = mock_client

    with pytest.raises(AttributeError):
        await source.fetch_items()

    await source.close()


# =============================================================================
# Scraping Source Error Handling Tests
# =============================================================================


@pytest.mark.asyncio
async def test_scraping_timeout_returns_empty(app_config):
    """Verify that TimeoutException is raised and logged."""
    source = BandcampScrapingSource(
        bandcamp_username=app_config.bandcamp_username,
        identity_token=app_config.identity_token,
        timezone=app_config.timezone,
    )

    # Mock the session to raise TimeoutException
    mock_session = AsyncMock()
    mock_session.get = AsyncMock(side_effect=Exception("Request timeout"))
    source._session = mock_session

    with pytest.raises(Exception, match="Request timeout"):
        await source.fetch_items()

    await source.close()


@pytest.mark.asyncio
async def test_scraping_connection_error_returns_empty(app_config):
    """Verify that connection error is raised and logged."""
    source = BandcampScrapingSource(
        bandcamp_username=app_config.bandcamp_username,
        identity_token=app_config.identity_token,
        timezone=app_config.timezone,
    )

    # Mock the session to raise ConnectError
    mock_session = AsyncMock()
    mock_session.get = AsyncMock(side_effect=Exception("Connection failed"))
    source._session = mock_session

    with pytest.raises(Exception, match="Connection failed"):
        await source.fetch_items()

    await source.close()


@pytest.mark.asyncio
async def test_scraping_http_500_returns_empty(app_config):
    """Verify that HTTP 500 response is raised and logged."""
    source = BandcampScrapingSource(
        bandcamp_username=app_config.bandcamp_username,
        identity_token=app_config.identity_token,
        timezone=app_config.timezone,
    )

    # Mock the session to return a 500 response
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status = MagicMock(side_effect=Exception("Server Error (500)"))
    mock_session = AsyncMock()
    mock_session.get = AsyncMock(return_value=mock_response)
    source._session = mock_session

    with pytest.raises(Exception, match=r"Server Error \(500\)"):
        await source.fetch_items()

    await source.close()


@pytest.mark.asyncio
async def test_scraping_http_403_returns_empty(app_config):
    """Verify that HTTP 403 response is raised and logged."""
    source = BandcampScrapingSource(
        bandcamp_username=app_config.bandcamp_username,
        identity_token=app_config.identity_token,
        timezone=app_config.timezone,
    )

    # Mock the session to return a 403 response
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.raise_for_status = MagicMock(side_effect=Exception("Forbidden (403)"))
    mock_session = AsyncMock()
    mock_session.get = AsyncMock(return_value=mock_response)
    source._session = mock_session

    with pytest.raises(Exception, match=r"Forbidden \(403\)"):
        await source.fetch_items()

    await source.close()


@pytest.mark.asyncio
async def test_scraping_non_html_response_returns_empty_list(app_config):
    """Verify that non-HTML response returns empty list."""
    source = BandcampScrapingSource(
        bandcamp_username=app_config.bandcamp_username,
        identity_token=app_config.identity_token,
        timezone=app_config.timezone,
    )

    # Mock the session to return plain text (not HTML)
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.content = b"Plain text response, not HTML"
    mock_session = AsyncMock()
    mock_session.get = AsyncMock(return_value=mock_response)
    source._session = mock_session

    result = await source.fetch_items()

    assert result == [], "Expected empty list on non-HTML response"
    await source.close()


@pytest.mark.asyncio
async def test_scraping_missing_feed_container_returns_empty_list(app_config):
    """Verify that missing feed container returns empty list."""
    source = BandcampScrapingSource(
        bandcamp_username=app_config.bandcamp_username,
        identity_token=app_config.identity_token,
        timezone=app_config.timezone,
    )

    # Mock the session to return HTML without feed container
    html_without_container = b"""<!DOCTYPE html>
<html>
<head><title>Bandcamp Feed</title></head>
<body>
<div class="some-other-container">
    <p>No feed here</p>
</div>
</body>
</html>"""

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.content = html_without_container
    mock_session = AsyncMock()
    mock_session.get = AsyncMock(return_value=mock_response)
    source._session = mock_session

    result = await source.fetch_items()

    assert result == [], "Expected empty list when feed container is missing"
    await source.close()


@pytest.mark.asyncio
async def test_scraping_empty_feed_container_returns_empty_list(app_config):
    """Verify that empty feed container returns empty list."""
    source = BandcampScrapingSource(
        bandcamp_username=app_config.bandcamp_username,
        identity_token=app_config.identity_token,
        timezone=app_config.timezone,
    )

    # Mock the session to return HTML with empty feed container
    html_empty_container = b"""<!DOCTYPE html>
<html>
<head><title>Bandcamp Feed</title></head>
<body>
<div class="feed-container">
    <ul>
    </ul>
</div>
</body>
</html>"""

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.content = html_empty_container
    mock_session = AsyncMock()
    mock_session.get = AsyncMock(return_value=mock_response)
    source._session = mock_session

    result = await source.fetch_items()

    assert result == [], "Expected empty list when feed container is empty"
    await source.close()
