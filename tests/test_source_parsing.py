"""
Tests for source parsing functionality.

Tests the internal parsing methods of bandcamp.py and bandcamp_api.py:
- _parse_date: Date parsing in scraping source
- _parse_datetime: Datetime parsing in API source
- feed_story_to_html_description: HTML description building
- _feed_story_to_feed_item: Item mapping
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from bs4 import BeautifulSoup

from bandcamp_async_api import FeedStory

from bandcamp_newsfeed_rss.sources.bandcamp import BandcampScrapingSource
from bandcamp_newsfeed_rss.sources.bandcamp_api import (
    BandcampAPISource,
    feed_story_to_html_description,
)
from bandcamp_newsfeed_rss.models import FeedItem


# =============================================================================
# Fixtures for Testing
# =============================================================================


@pytest.fixture
def scraping_source():
    """Create a BandcampScrapingSource instance for testing."""
    return BandcampScrapingSource(
        bandcamp_username="testuser",
        identity_token="test_token",
        timezone=ZoneInfo("Europe/London"),
    )


@pytest.fixture
def api_source():
    """Create a BandcampAPISource instance for testing."""
    return BandcampAPISource(
        identity_token="test_token",
        bandcamp_username="testuser",
        timezone=ZoneInfo("Europe/London"),
    )


# =============================================================================
# Scraping Source — Date Parsing Tests (_parse_date)
# =============================================================================


class TestBandcampScrapingDateParsing:
    """Tests for the _parse_date method in BandcampScrapingSource."""

    def test_parse_date_hours_ago(self, scraping_source):
        """Input '3 hours ago' should return datetime approximately 3 hours before now."""
        result = scraping_source._parse_date("3 hours ago")

        # Result should be a datetime
        assert isinstance(result, datetime)

        # Should be approximately 3 hours ago
        expected_min = datetime.now(tz=scraping_source.timezone) - timedelta(hours=3, minutes=1)
        expected_max = datetime.now(tz=scraping_source.timezone) - timedelta(hours=2, minutes=59)
        assert expected_min <= result <= expected_max, (
            f"Expected datetime between {expected_min} and {expected_max}, got {result}"
        )

    def test_parse_date_one_hour_ago(self, scraping_source):
        """Input '1 hour ago' should return datetime approximately 1 hour before now."""
        result = scraping_source._parse_date("1 hour ago")

        assert isinstance(result, datetime)

        # Should be approximately 1 hour ago
        expected_min = datetime.now(tz=scraping_source.timezone) - timedelta(hours=1, minutes=1)
        expected_max = datetime.now(tz=scraping_source.timezone) - timedelta(minutes=59)
        assert expected_min <= result <= expected_max, (
            f"Expected datetime between {expected_min} and {expected_max}, got {result}"
        )

    def test_parse_date_minutes_ago(self, scraping_source):
        """Input '45 minutes ago' should return datetime approximately 45 minutes before now."""
        result = scraping_source._parse_date("45 minutes ago")

        assert isinstance(result, datetime)

        # Should be approximately 45 minutes ago
        expected_min = datetime.now(tz=scraping_source.timezone) - timedelta(minutes=46)
        expected_max = datetime.now(tz=scraping_source.timezone) - timedelta(minutes=44)
        assert expected_min <= result <= expected_max, (
            f"Expected datetime between {expected_min} and {expected_max}, got {result}"
        )

    def test_parse_date_yesterday(self, scraping_source):
        """Input 'yesterday' should return datetime approximately 24 hours before now."""
        result = scraping_source._parse_date("yesterday")

        assert isinstance(result, datetime)

        # Should be approximately 1 day ago
        expected_min = datetime.now(tz=scraping_source.timezone) - timedelta(days=1, minutes=1)
        expected_max = datetime.now(tz=scraping_source.timezone) - timedelta(hours=23, minutes=59)
        assert expected_min <= result <= expected_max, (
            f"Expected datetime between {expected_min} and {expected_max}, got {result}"
        )

    def test_parse_date_absolute_lowercase(self, scraping_source):
        """Input 'jan 28, 2026' should return datetime(2026, 1, 28, ...)."""
        result = scraping_source._parse_date("jan 28, 2026")

        assert isinstance(result, datetime)
        assert result.year == 2026
        assert result.month == 1
        assert result.day == 28

    def test_parse_date_absolute_uppercase(self, scraping_source):
        """Input 'Jan 28, 2026' should return datetime(2026, 1, 28, ...)."""
        result = scraping_source._parse_date("Jan 28, 2026")

        assert isinstance(result, datetime)
        assert result.year == 2026
        assert result.month == 1
        assert result.day == 28

    def test_parse_date_invalid_falls_back_to_now(self, scraping_source):
        """Unrecognised string should return datetime close to datetime.now()."""
        result = scraping_source._parse_date("invalid date string")

        assert isinstance(result, datetime)

        # Should be close to now
        now = datetime.now(tz=scraping_source.timezone)
        diff = abs((now - result).total_seconds())
        assert diff < 5, f"Expected datetime close to now, got {result} (diff: {diff}s)"


# =============================================================================
# API Source — Datetime Parsing Tests (_parse_datetime)
# =============================================================================


class TestBandcampAPIDatetimeParsing:
    """Tests for the _parse_datetime method in BandcampAPISource."""

    def test_parse_datetime_iso_format(self, api_source):
        """ISO 8601 string should fall back to now (not supported by parsedate_to_datetime)."""
        result = api_source._parse_datetime("2026-01-28T14:30:00")

        assert isinstance(result, datetime)

        # Should fall back to now since ISO format is not supported
        now = datetime.now(tz=api_source.timezone)
        diff = abs((now - result).total_seconds())
        assert diff < 5, f"Expected fallback datetime close to now, got {result} (diff: {diff}s)"

    def test_parse_datetime_with_utc_timezone(self, api_source):
        """UTC timezone suffix should fall back to now (not supported)."""
        result = api_source._parse_datetime("2026-01-28T14:30:00Z")

        assert isinstance(result, datetime)

        # Should fall back to now since this format is not supported
        now = datetime.now(tz=api_source.timezone)
        diff = abs((now - result).total_seconds())
        assert diff < 5, f"Expected fallback datetime close to now, got {result} (diff: {diff}s)"

    def test_parse_datetime_with_offset_timezone(self, api_source):
        """Offset timezone should fall back to now (not supported)."""
        result = api_source._parse_datetime("2026-01-28T14:30:00+02:00")

        assert isinstance(result, datetime)

        # Should fall back to now since this format is not supported
        now = datetime.now(tz=api_source.timezone)
        diff = abs((now - result).total_seconds())
        assert diff < 5, f"Expected fallback datetime close to now, got {result} (diff: {diff}s)"

    def test_parse_datetime_invalid_falls_back(self, api_source):
        """Invalid string should return fallback value close to now, not raise."""
        result = api_source._parse_datetime("invalid datetime string")

        assert isinstance(result, datetime)

        # Should be close to now
        now = datetime.now(tz=api_source.timezone)
        diff = abs((now - result).total_seconds())
        assert diff < 5, f"Expected fallback datetime close to now, got {result} (diff: {diff}s)"

    def test_parse_datetime_rfc_2822_format(self, api_source):
        """RFC 2822 format '15 Jan 2026 10:30:00 GMT' should parse correctly."""
        result = api_source._parse_datetime("15 Jan 2026 10:30:00 GMT")

        assert isinstance(result, datetime)
        assert result.year == 2026
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 10
        assert result.minute == 30


# =============================================================================
# API Source — HTML Description Building Tests
# =============================================================================


class TestFeedStoryToHtmlDescription:
    """Tests for the feed_story_to_html_description function."""

    def test_html_description_nr_story_type(self):
        """story_type='nr' (new release) produces expected HTML structure."""
        story = FeedStory(
            story_type="nr",
            fan_id=123456,
            item_id=111111,
            item_type="a",
            tralbum_id=111111,
            tralbum_type="a",
            band_id=100001,
            story_date="15 Jan 2026 10:30:00 GMT",
            item_title="Test Album",
            item_url="https://artist.bandcamp.com/album/test-album",
            item_art_url="https://example.com/art.jpg",
            band_name="Test Artist",
            band_url="https://artist.bandcamp.com",
            album_title="Test Album",
            tags=[{"url": "https://bandcamp.com/tags/rock", "name": "rock"}],
        )

        result = feed_story_to_html_description(story)

        assert isinstance(result, str)
        assert "an album" in result, "Expected 'an album' in HTML for nr type"
        assert "Test Artist" in result
        assert "Test Album" in result

    def test_html_description_np_story_type(self):
        """story_type='np' (new post) produces expected HTML structure."""
        story = FeedStory(
            story_type="np",
            fan_id=123456,
            item_id=222222,
            item_type="a",
            tralbum_id=222222,
            tralbum_type="a",
            band_id=100002,
            story_date="14 Jan 2026 15:45:00 GMT",
            item_title="Purchase Album",
            item_url="https://artist.bandcamp.com/album/purchase-album",
            item_art_url="https://example.com/art2.jpg",
            band_name="Another Artist",
            band_url="https://another.bandcamp.com",
            album_title="Purchase Album",
            tags=[],
        )

        result = feed_story_to_html_description(story)

        assert isinstance(result, str)
        assert "a purchase" in result, "Expected 'a purchase' in HTML for np type"
        assert "Another Artist" in result

    def test_html_description_fp_story_type(self):
        """story_type='fp' (featured post) produces expected HTML structure."""
        story = FeedStory(
            story_type="fp",
            fan_id=123456,
            item_id=333333,
            item_type="p",
            tralbum_id=333333,
            tralbum_type="p",
            band_id=100003,
            story_date="13 Jan 2026 20:00:00 GMT",
            item_title="Featured Merch",
            item_url="https://artist.bandcamp.com/merch/featured-merch",
            item_art_url="https://example.com/art3.jpg",
            band_name="Featured Artist",
            band_url="https://featured.bandcamp.com",
            tags=[],
        )

        result = feed_story_to_html_description(story)

        assert isinstance(result, str)
        assert "a featured purchase" in result, "Expected 'a featured purchase' in HTML for fp type"
        assert "Featured Artist" in result

    def test_html_description_missing_tags(self):
        """Story without tags field should render without error."""
        story = FeedStory(
            story_type="nr",
            fan_id=123456,
            item_id=111111,
            item_type="a",
            tralbum_id=111111,
            tralbum_type="a",
            band_id=100001,
            story_date="15 Jan 2026 10:30:00 GMT",
            item_title="Test Album",
            item_url="https://artist.bandcamp.com/album/test-album",
            band_name="Test Artist",
            band_url="https://artist.bandcamp.com",
            album_title="Test Album",
        )

        result = feed_story_to_html_description(story)

        assert isinstance(result, str)
        assert "Test Artist" in result
        assert "Test Album" in result

    def test_html_description_missing_featured_track(self):
        """Story without featured_track_title should render without error."""
        story = FeedStory(
            story_type="nr",
            fan_id=123456,
            item_id=111111,
            item_type="a",
            tralbum_id=111111,
            tralbum_type="a",
            band_id=100001,
            story_date="15 Jan 2026 10:30:00 GMT",
            item_title="Test Album",
            item_url="https://artist.bandcamp.com/album/test-album",
            item_art_url="https://example.com/art.jpg",
            band_name="Test Artist",
            band_url="https://artist.bandcamp.com",
            album_title="Test Album",
            tags=[],
        )

        result = feed_story_to_html_description(story)

        assert isinstance(result, str)
        assert "Test Artist" in result
        # Should not contain featured track section
        assert "featured_track" not in result.lower()

    def test_html_description_output_is_valid_html(self):
        """Output should be parseable by BeautifulSoup."""
        story = FeedStory(
            story_type="nr",
            fan_id=123456,
            item_id=111111,
            item_type="a",
            tralbum_id=111111,
            tralbum_type="a",
            band_id=100001,
            story_date="15 Jan 2026 10:30:00 GMT",
            item_title="Test Album",
            item_url="https://artist.bandcamp.com/album/test-album",
            item_art_url="https://example.com/art.jpg",
            band_name="Test Artist",
            band_url="https://artist.bandcamp.com",
            album_title="Test Album",
            tags=[{"url": "https://bandcamp.com/tags/rock", "name": "rock"}],
        )

        result = feed_story_to_html_description(story)

        # Should be parseable without errors
        soup = BeautifulSoup(result, "html.parser")
        assert soup is not None

        # Should have expected structure
        assert soup.find("div", class_="story-body") is not None


# =============================================================================
# Item Parsing Tests
# =============================================================================


class TestBandcampScrapingItemParsing:
    """Tests for item parsing in BandcampScrapingSource."""

    def test_parse_item_complete_data(self):
        """Feed item with all fields present should produce FeedItem with all fields."""
        source = BandcampScrapingSource(
            bandcamp_username="testuser",
            identity_token="test_token",
            timezone=ZoneInfo("Europe/London"),
        )

        html = """<li class="story nr">
            <div class="story-date">jan 15, 2026</div>
            <a class="artist-name" href="https://artist.bandcamp.com">Test Artist</a>
            <a class="item-link" href="https://artist.bandcamp.com/album/test-album">Test Album</a>
            <img class="tralbum-art-large" src="https://example.com/art.jpg"/>
            <div class="collection-item-title">Test Album</div>
        </li>"""

        soup = BeautifulSoup(html, "html.parser")
        item = soup.find("li")

        result = source._parse_item(item)

        assert result is not None
        assert isinstance(result, FeedItem)
        assert result.title == "Test Album by Test Artist"
        assert result.link == "https://artist.bandcamp.com/album/test-album"
        assert result.author == "Test Artist"
        assert result.guid == "https://artist.bandcamp.com/album/test-album"
        assert result.enclosure_url == "https://example.com/art.jpg"

    def test_parse_item_missing_optional_fields(self):
        """Feed item with optional fields absent should have None for those fields."""
        source = BandcampScrapingSource(
            bandcamp_username="testuser",
            identity_token="test_token",
            timezone=ZoneInfo("Europe/London"),
        )

        # HTML with missing elements
        html = """<li class="story nr">
            <div class="story-date">jan 15, 2026</div>
        </li>"""

        soup = BeautifulSoup(html, "html.parser")
        item = soup.find("li")

        result = source._parse_item(item)

        # Should return None due to missing required fields
        assert result is None

    def test_parse_item_url_cleaning(self):
        """URL with query parameters should be cleaned (query stripped)."""
        source = BandcampScrapingSource(
            bandcamp_username="testuser",
            identity_token="test_token",
            timezone=ZoneInfo("Europe/London"),
        )

        html = """<li class="story nr">
            <div class="story-date">jan 15, 2026</div>
            <a class="artist-name" href="https://artist.bandcamp.com">Test Artist</a>
            <a class="item-link" href="https://artist.bandcamp.com/album/test-album?utm_source=tracking">Test Album</a>
            <img class="tralbum-art-large" src="https://example.com/art.jpg"/>
            <div class="collection-item-title">Test Album</div>
        </li>"""

        soup = BeautifulSoup(html, "html.parser")
        item = soup.find("li")

        result = source._parse_item(item)

        assert result is not None
        # Query parameters should be stripped
        assert "?" not in result.link, f"Expected clean URL without query, got {result.link}"
        assert result.link == "https://artist.bandcamp.com/album/test-album"


class TestBandcampAPIItemMapping:
    """Tests for FeedStory to FeedItem mapping in BandcampAPISource."""

    def test_feed_story_to_feed_item_mapping(self, api_source):
        """API FeedStory model should map to FeedItem with correct field assignments."""
        story = FeedStory(
            story_type="nr",
            fan_id=123456,
            item_id=111111,
            item_type="a",
            tralbum_id=111111,
            tralbum_type="a",
            band_id=100001,
            story_date="15 Jan 2026 10:30:00 GMT",
            item_title="Test Album",
            item_url="https://artist.bandcamp.com/album/test-album",
            item_art_url="https://example.com/art.jpg",
            band_name="Test Artist",
            band_url="https://artist.bandcamp.com",
            album_title="Test Album",
            tags=[{"url": "https://bandcamp.com/tags/rock", "name": "rock"}],
            featured_track_title="First Track",
        )

        result = api_source._feed_story_to_feed_item(story)

        assert isinstance(result, FeedItem)
        assert result.title == "Test Album by Test Artist"
        assert result.link == "https://artist.bandcamp.com/album/test-album"
        assert result.author == "Test Artist"
        assert result.guid == "https://artist.bandcamp.com/album/test-album"
        assert result.enclosure_url == "https://example.com/art.jpg"
        assert result.description is not None
        assert "Test Album" in result.description
        assert "Test Artist" in result.description

    def test_feed_story_to_feed_item_with_minimal_fields(self, api_source):
        """FeedStory with minimal fields should map correctly."""
        story = FeedStory(
            story_type="nr",
            fan_id=123456,
            item_id=111111,
            item_type="a",
            tralbum_id=111111,
            tralbum_type="a",
            band_id=100001,
            story_date="15 Jan 2026 10:30:00 GMT",
            item_title="Minimal Album",
            item_url="https://artist.bandcamp.com/album/minimal-album",
            band_name="Minimal Artist",
            band_url="https://artist.bandcamp.com",
        )

        result = api_source._feed_story_to_feed_item(story)

        assert isinstance(result, FeedItem)
        assert result.title == "Minimal Album by Minimal Artist"
        assert result.link == "https://artist.bandcamp.com/album/minimal-album"
        assert result.author == "Minimal Artist"

    def test_feed_story_to_feed_item_uses_album_title(self, api_source):
        """FeedStory with both item_title and album_title should use album_title."""
        story = FeedStory(
            story_type="nr",
            fan_id=123456,
            item_id=111111,
            item_type="a",
            tralbum_id=111111,
            tralbum_type="a",
            band_id=100001,
            story_date="15 Jan 2026 10:30:00 GMT",
            item_title="Item Title",
            item_url="https://artist.bandcamp.com/album/test-album",
            item_art_url="https://example.com/art.jpg",
            band_name="Test Artist",
            band_url="https://artist.bandcamp.com",
            album_title="Album Title",
        )

        result = api_source._feed_story_to_feed_item(story)

        assert isinstance(result, FeedItem)
        # Album title should be used in the HTML description
        assert "Album Title" in result.description
