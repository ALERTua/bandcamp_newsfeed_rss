"""Bandcamp API feed source."""

import logging
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import TYPE_CHECKING, Self

from bandcamp_async_api import BandcampAPIClient, FeedStory

from ..models import FeedItem
from ..config import BANDCAMP_FILTER_PREORDERS


if TYPE_CHECKING:
    from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)


def feed_story_to_html_description(story: FeedStory, pub_date: datetime | None = None) -> str:
    """
    Generate an HTML description for a FeedStory matching the scraper structure.

    Args:
        story: The FeedStory to convert.
        pub_date: The publication date of the feed item.

    Returns:
        An HTML string describing the feed story.

    """
    formatted_date = pub_date or story.story_date

    # Determine story type label
    story_type_label = {
        "nr": "An album",
        "np": "A purchase",
        "fp": "A featured purchase",
    }.get(story.story_type, "a release")

    # Build story title section
    story_title = f"""<div class="story-title">
<div class="story-date">{formatted_date}</div>
{story_type_label} by <a class="artist-name" href="{story.band_url}" target="_blank">{story.band_name}</a>.
</div>"""

    # Build album art section
    art_html = ""
    if story.item_art_url:
        art_html = f"""<div class="tralbum-art-container">
<img class="tralbum-art-large" src="{story.item_art_url}"/>
</div>"""

    # Build item details section
    item_title = story.album_title or story.item_title or ""
    tralbum_details = f"""<div class="tralbum-details">
<a class="item-link" href="{story.item_url}" target="_blank">
<div class="collection-item-title">{item_title}</div>
<div class="collection-item-artist">by {story.band_name}</div>
</a>"""

    # Add featured track if available
    if story.featured_track_title:
        tralbum_details += f"""
<div class="collection-item-fav-track cf">
<span class="favoriteTrackLabel">featured track: <span class="fav-track-title">{story.featured_track_title}</span>
</span></div>"""

    tralbum_details += "\n</div>"

    # Build tags section
    tags_html = ""
    if story.tags:
        # Tags are list of dicts with 'url' and 'name' keys
        tag_links = []
        for tag in story.tags:
            if isinstance(tag, dict):
                tag_url = tag.get("url", "")
                tag_name = tag.get("name", "")
                if tag_name:
                    tag_links.append(f'<a href="{tag_url}">{tag_name}</a>')
        if tag_links:
            tags_html = f"""<div class="collection-item-tags">tags: {", ".join(tag_links)}</div>"""

    # Assemble the full HTML
    return f"""<div class="story-body">
{story_title}
<div class="tralbum-wrapper cf">
<div class="tralbum-wrapper-col1">
{art_html}
{tralbum_details}
</div>
</div>
<div class="story-footer">
{tags_html}
</div>
</div>"""


class BandcampAPISource:
    """Bandcamp feed source using the official Bandcamp API."""

    def __init__(
        self,
        identity_token: str,
        bandcamp_username: str,
        timezone: ZoneInfo,
    ):
        """
        Initialize the Bandcamp API source.

        Args:
            identity_token: Bandcamp identity token for authentication.
                           If not provided, will use IDENTITY from config.
            bandcamp_username: Bandcamp username to fetch feed for.
            timezone: Timezone to use for parsing dates.

        """
        self._identity_token = identity_token
        self._bandcamp_username = bandcamp_username
        self.timezone = timezone
        self._client = BandcampAPIClient(identity_token=self._identity_token)
        self._feed_url = f"https://bandcamp.com/{self._bandcamp_username}/feed"

    @property
    def feed_url(self) -> str:
        """Return the URL of the feed."""
        return self._feed_url

    @property
    def feed_title(self) -> str:
        """Return the title of the feed."""
        return f"{self._bandcamp_username} Bandcamp Feed"

    async def fetch_items(self) -> list[FeedItem]:
        """
        Fetch items from the Bandcamp API feed.

        Returns:
            List of FeedItem instances from the user's feed.

        Raises:
            BandcampMustBeLoggedInError: If identity token is not set.

        """
        try:
            feed_response = await self._client.get_feed()
        except Exception:
            logger.exception("Failed to fetch Bandcamp API feed")
            raise

        stories = feed_response.stories[::-1]
        if BANDCAMP_FILTER_PREORDERS:
            stories = [_ for _ in stories if not _.is_preorder]

        feed_items = [self._feed_story_to_feed_item(_) for _ in stories]

        logger.info(f"Fetched {len(feed_items)} items from Bandcamp API feed")
        return feed_items

    def _parse_datetime(self, date_str: str) -> datetime:
        """Parse a datetime string from Bandcamp API into a datetime object."""
        try:  # '09 Dec 2025 13:57:15 GMT'
            parsed_dt = parsedate_to_datetime(date_str)

            # If already has timezone, convert to our timezone; otherwise replace
            if parsed_dt.tzinfo is not None:
                return parsed_dt.astimezone(self.timezone)

            return parsed_dt.replace(tzinfo=self.timezone)

        except Exception as e:  # noqa: BLE001
            logger.warning(f"Failed to parse datetime: {date_str} - {e}")
            return datetime.now(tz=self.timezone)

    def _feed_story_to_feed_item(self, story: FeedStory) -> FeedItem:
        """
        Convert a FeedStory from the Bandcamp API to a FeedItem.

        Args:
            story: The FeedStory to convert.

        Returns:
            A FeedItem instance with data mapped from the FeedStory.

        """
        pub_date = self._parse_datetime(story.story_date)
        description = feed_story_to_html_description(story, pub_date=pub_date)
        title = f"{story.item_title} by {story.band_name}"
        tags = []
        if story.tags:
            tags = [_.get("name", "") for _ in story.tags]
            tags = [_ for _ in tags if _]

        return FeedItem(
            title=title,
            link=story.item_url,
            author=story.band_name,
            description=description,
            pub_date=pub_date,
            guid=story.item_url,
            enclosure_url=story.item_art_url,
            tags=tags,
        )

    async def close(self) -> None:
        """Close the API client."""
        # TODO: use session_close() after the next release
        if self._client._session:  # noqa: SLF001
            await self._client._session.close()  # noqa: SLF001

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()
