"""Pytest configuration and fixtures."""

from dataclasses import dataclass
from datetime import datetime, UTC
from zoneinfo import ZoneInfo

import pytest

from bandcamp_async_api import FeedStory
from bandcamp_newsfeed_rss.cache import clear_cache
from bandcamp_newsfeed_rss.models import FeedItem


# =============================================================================
# Existing Fixtures
# =============================================================================


@pytest.fixture
def anyio_backend():
    """Use asyncio as the async backend for pytest-anyio."""
    return "asyncio"


@pytest.fixture
def clean_cache():
    """Provide a clean, empty cache for each test."""
    clear_cache()
    yield
    clear_cache()


# Configure pytest-asyncio
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers",
        "asyncio: mark test as async",
    )


# =============================================================================
# Shared Fixtures
# =============================================================================


@dataclass(frozen=True)
class AppConfig:
    """Test configuration object mimicking the app's config values."""

    bandcamp_username: str
    identity_token: str
    timezone: ZoneInfo


@pytest.fixture(scope="session")
def app_config() -> AppConfig:
    """Provide a Config instance with test-safe values."""
    return AppConfig(
        bandcamp_username="testuser",
        identity_token="test_identity_token_12345",
        timezone=ZoneInfo("Europe/London"),
    )


@pytest.fixture(scope="session")
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
        FeedItem(
            title="Album Title 3 by Artist Three",
            link="https://artist3.bandcamp.com/album/album-title-3",
            author="Artist Three",
            description="<div class='test-description'>Test album description 3</div>",
            pub_date=datetime(2026, 1, 13, 20, 0, tzinfo=UTC),
            guid="https://artist3.bandcamp.com/album/album-title-3",
            enclosure_url="https://example.com/art3.jpg",
            enclosure_type="image/jpeg",
        ),
    ]


@pytest.fixture(scope="session")
def sample_feed_item_minimal() -> FeedItem:
    """Provide a FeedItem with only required fields."""
    return FeedItem(
        title="Minimal Album by Minimal Artist",
        link="https://minimal.bandcamp.com/album/minimal-album",
        author="Minimal Artist",
        description="<div>Minimal description</div>",
        pub_date=datetime(2026, 1, 10, 12, 0, tzinfo=UTC),
    )


# =============================================================================
# API Fixtures
# =============================================================================


@pytest.fixture(scope="session")
def sample_api_response_full() -> dict:
    """Valid JSON response with all fields, 3 story objects."""  # noqa: D401
    return {
        "stories": [
            {
                "story_type": "nr",
                "fan_id": 123456,
                "item_id": 111111,
                "item_type": "a",
                "tralbum_id": 111111,
                "tralbum_type": "a",
                "band_id": 100001,
                "story_date": "15 Jan 2026 10:30:00 GMT",
                "item_title": "Album Title 1",
                "item_url": "https://artist1.bandcamp.com/album/album-title-1",
                "item_art_url": "https://example.com/art1.jpg",
                "item_art_id": 111111,
                "band_name": "Artist One",
                "band_url": "https://artist1.bandcamp.com",
                "album_id": 111111,
                "album_title": "Album Title 1",
                "genre_id": 1,
                "tags": [{"url": "https://bandcamp.com/tags/rock", "name": "rock"}],
                "is_purchasable": True,
                "price": 10.0,
                "currency": "USD",
                "is_preorder": False,
                "num_streamable_tracks": 8,
                "also_collected_count": 50,
                "featured_track": 1,
                "featured_track_title": "Track One",
                "featured_track_duration": 180.5,
                "featured_track_number": 1,
                "featured_track_encodings_id": 111,
            },
            {
                "story_type": "np",
                "fan_id": 123456,
                "item_id": 222222,
                "item_type": "a",
                "tralbum_id": 222222,
                "tralbum_type": "a",
                "band_id": 100002,
                "story_date": "14 Jan 2026 15:45:00 GMT",
                "item_title": "Album Title 2",
                "item_url": "https://artist2.bandcamp.com/album/album-title-2",
                "item_art_url": "https://example.com/art2.jpg",
                "item_art_id": 222222,
                "band_name": "Artist Two",
                "band_url": "https://artist2.bandcamp.com",
                "album_id": 222222,
                "album_title": "Album Title 2",
                "genre_id": 2,
                "tags": [{"url": "https://bandcamp.com/tags/electronic", "name": "electronic"}],
                "is_purchasable": True,
                "price": 15.0,
                "currency": "EUR",
                "is_preorder": False,
                "num_streamable_tracks": 10,
                "also_collected_count": 100,
            },
            {
                "story_type": "fp",
                "fan_id": 123456,
                "item_id": 333333,
                "item_type": "p",
                "tralbum_id": 333333,
                "tralbum_type": "p",
                "band_id": 100003,
                "story_date": "13 Jan 2026 20:00:00 GMT",
                "item_title": "Merch Package",
                "item_url": "https://artist3.bandcamp.com/merch/merch-package",
                "item_art_url": "https://example.com/art3.jpg",
                "item_art_id": 333333,
                "band_name": "Artist Three",
                "band_url": "https://artist3.bandcamp.com",
                "album_id": None,
                "album_title": None,
                "genre_id": 3,
                "tags": [],
                "is_purchasable": True,
                "price": 25.0,
                "currency": "GBP",
                "is_preorder": True,
                "num_streamable_tracks": None,
                "also_collected_count": 25,
            },
        ],
    }


@pytest.fixture(scope="session")
def sample_api_response_minimal() -> dict:
    """Valid JSON with only required fields, 1 story."""  # noqa: D401
    return {
        "stories": [
            {
                "story_type": "nr",
                "fan_id": 123456,
                "item_id": 111111,
                "item_type": "a",
                "tralbum_id": 111111,
                "tralbum_type": "a",
                "band_id": 100001,
                "story_date": "15 Jan 2026 10:30:00 GMT",
                "item_title": "Minimal Album",
                "item_url": "https://artist.bandcamp.com/album/minimal-album",
                "band_name": "Minimal Artist",
                "band_url": "https://artist.bandcamp.com",
            },
        ],
    }


@pytest.fixture(scope="session")
def sample_api_response_empty_stories() -> dict:
    """Valid JSON with stories: [] (empty array)."""  # noqa: D401
    return {"stories": []}


@pytest.fixture(scope="session")
def sample_feed_story_nr() -> FeedStory:
    """New-release type story with all fields."""
    return FeedStory(
        story_type="nr",
        fan_id=123456,
        item_id=111111,
        item_type="a",
        tralbum_id=111111,
        tralbum_type="a",
        band_id=100001,
        story_date="15 Jan 2026 10:30:00 GMT",
        item_title="Album Title 1",
        item_url="https://artist1.bandcamp.com/album/album-title-1",
        item_art_url="https://example.com/art1.jpg",
        item_art_id=111111,
        band_name="Artist One",
        band_url="https://artist1.bandcamp.com",
        album_id=111111,
        album_title="Album Title 1",
        genre_id=1,
        tags=[{"url": "https://bandcamp.com/tags/rock", "name": "rock"}],
        is_purchasable=True,
        price=10.0,
        currency="USD",
        is_preorder=False,
        num_streamable_tracks=8,
        also_collected_count=50,
        featured_track=1,
        featured_track_title="Track One",
        featured_track_duration=180.5,
        featured_track_number=1,
        featured_track_encodings_id=111,
    )


@pytest.fixture(scope="session")
def sample_feed_story_np() -> FeedStory:
    """New-post type story with all fields."""
    return FeedStory(
        story_type="np",
        fan_id=123456,
        item_id=222222,
        item_type="a",
        tralbum_id=222222,
        tralbum_type="a",
        band_id=100002,
        story_date="14 Jan 2026 15:45:00 GMT",
        item_title="Album Title 2",
        item_url="https://artist2.bandcamp.com/album/album-title-2",
        item_art_url="https://example.com/art2.jpg",
        item_art_id=222222,
        band_name="Artist Two",
        band_url="https://artist2.bandcamp.com",
        album_id=222222,
        album_title="Album Title 2",
        genre_id=2,
        tags=[{"url": "https://bandcamp.com/tags/electronic", "name": "electronic"}],
        is_purchasable=True,
        price=15.0,
        currency="EUR",
        is_preorder=False,
        num_streamable_tracks=10,
        also_collected_count=100,
    )


@pytest.fixture(scope="session")
def sample_feed_story_missing_optional() -> FeedStory:
    """Story missing optional fields."""
    return FeedStory(
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


# =============================================================================
# Scraping Fixtures
# =============================================================================


@pytest.fixture(scope="session")
def sample_html_feed_page() -> str:
    """Full HTML page with 3 feed items in .feed-container."""
    return """<!DOCTYPE html>
<html>
<head><title>Bandcamp Feed</title></head>
<body>
<div class="feed-container">
    <ul>
        <li class="story nr">
            <div class="story-title">
                <div class="story-date">3 hours ago</div>
                <a class="artist-name" href="https://artist1.bandcamp.com" target="_blank">Artist One</a> an album.
            </div>
            <div class="tralbum-art-container">
                <img class="tralbum-art-large" src="https://example.com/art1.jpg"/>
            </div>
            <div class="tralbum-details">
                <a class="item-link" href="https://artist1.bandcamp.com/album/album-title-1" target="_blank">
                    <div class="collection-item-title">Album Title 1</div>
                    <div class="collection-item-artist">by Artist One</div>
                </a>
                <div class="collection-item-fav-track cf">
                    <span class="favoriteTrackLabel">featured track: <span class="fav-track-title">Track One</span></span>
                </div>
            </div>
            <div class="story-footer">
                <div class="collection-item-tags">tags: <a href="https://bandcamp.com/tags/rock">rock</a></div>
            </div>
        </li>
        <li class="story np">
            <div class="story-title">
                <div class="story-date">1 day ago</div>
                <a class="artist-name" href="https://artist2.bandcamp.com" target="_blank">Artist Two</a> a purchase.
            </div>
            <div class="tralbum-art-container">
                <img class="tralbum-art-large" src="https://example.com/art2.jpg"/>
            </div>
            <div class="tralbum-details">
                <a class="item-link" href="https://artist2.bandcamp.com/album/album-title-2" target="_blank">
                    <div class="collection-item-title">Album Title 2</div>
                    <div class="collection-item-artist">by Artist Two</div>
                </a>
            </div>
            <div class="story-footer">
                <div class="collection-item-tags">tags: <a href="https://bandcamp.com/tags/electronic">electronic</a></div>
            </div>
        </li>
        <li class="story nr">
            <div class="story-title">
                <div class="story-date">jan 15, 2026</div>
                <a class="artist-name" href="https://artist3.bandcamp.com" target="_blank">Artist Three</a> an album.
            </div>
            <div class="tralbum-art-container">
                <img class="tralbum-art-large" src="https://example.com/art3.jpg"/>
            </div>
            <div class="tralbum-details">
                <a class="item-link" href="https://artist3.bandcamp.com/album/album-title-3" target="_blank">
                    <div class="collection-item-title">Album Title 3</div>
                    <div class="collection-item-artist">by Artist Three</div>
                </a>
            </div>
            <div class="story-footer">
                <div class="collection-item-tags">tags: <a href="https://bandcamp.com/tags/jazz">jazz</a></div>
            </div>
        </li>
    </ul>
</div>
</body>
</html>"""  # noqa: E501


@pytest.fixture(scope="session")
def sample_html_feed_minimal() -> str:
    """HTML with 1 feed item, minimum required elements."""
    return """<!DOCTYPE html>
<html>
<head><title>Bandcamp Feed</title></head>
<body>
<div class="feed-container">
    <ul>
        <li class="story nr">
            <div class="story-title">
                <div class="story-date">2 hours ago</div>
                <a class="artist-name" href="https://minimal.bandcamp.com" target="_blank">Minimal Artist</a> an album.
            </div>
            <div class="tralbum-art-container">
                <img class="tralbum-art-large" src="https://example.com/minimal.jpg"/>
            </div>
            <div class="tralbum-details">
                <a class="item-link" href="https://minimal.bandcamp.com/album/minimal-album" target="_blank">
                    <div class="collection-item-title">Minimal Album</div>
                    <div class="collection-item-artist">by Minimal Artist</div>
                </a>
            </div>
        </li>
    </ul>
</div>
</body>
</html>"""


@pytest.fixture(scope="session")
def sample_html_no_feed_container() -> str:
    """Valid HTML but missing .feed-container."""  # noqa: D401
    return """<!DOCTYPE html>
<html>
<head><title>Bandcamp Feed</title></head>
<body>
<div class="some-other-container">
    <p>No feed here</p>
</div>
</body>
</html>"""


@pytest.fixture(scope="session")
def sample_html_empty_feed_container() -> str:
    """HTML with .feed-container but no items."""
    return """<!DOCTYPE html>
<html>
<head><title>Bandcamp Feed</title></head>
<body>
<div class="feed-container">
    <ul>
    </ul>
</div>
</body>
</html>"""
