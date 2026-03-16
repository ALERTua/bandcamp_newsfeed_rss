"""Bandcamp scraping feed source."""

import logging
import re
from datetime import datetime, timedelta
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from curl_cffi.requests import AsyncSession
from zoneinfo import ZoneInfo

from .protocol import FeedItem
from .registry import register_source

logger = logging.getLogger(__name__)


@register_source("scraping")
class BandcampScrapingSource:
    """Bandcamp feed source using web scraping."""

    def __init__(
        self,
        username: str,
        identity: str,
        timezone: ZoneInfo | None = None,
    ):
        self.username = username
        self.identity = identity
        self.timezone = timezone or ZoneInfo("Europe/London")
        self._url = f"https://bandcamp.com/{username}/feed"
        self._cookies = {"identity": identity}
        self._session = AsyncSession()

    @property
    def feed_url(self) -> str:
        return self._url

    @property
    def feed_title(self) -> str:
        return f"Bandcamp {self.username} Feed"

    async def fetch_items(self) -> list[FeedItem]:
        try:
            response = await self._session.get(
                self._url,
                cookies=self._cookies,
                impersonate="chrome",
                timeout=30,
            )
            response.raise_for_status()
        except Exception:
            logger.exception("Failed to fetch Bandcamp feed")
            raise

        soup = BeautifulSoup(response.content, "html.parser")
        items = soup.find_all("li", class_="story nr")
        items = items[::-1]  # Reverse to get chronological order

        feed_items = []
        for item in items:
            feed_item = self._parse_item(item)
            if feed_item:
                feed_items.append(feed_item)

        logger.info(f"Fetched {len(feed_items)} items from Bandcamp feed")
        return feed_items

    async def close(self) -> None:
        """Close the async session."""
        await self._session.close()

    def _parse_item(self, item: BeautifulSoup) -> FeedItem | None:
        try:
            title_elem = item.find("div", class_="collection-item-title")
            artist_elem = item.find("a", class_="artist-name")
            album_link_elem = item.find("a", class_="item-link")
            cover_image_elem = item.find("img", class_="tralbum-art-large")
            release_date_elem = item.find("div", class_="story-date")

            if not all([title_elem, artist_elem, album_link_elem, cover_image_elem, release_date_elem]):
                return None

            title = title_elem.text.strip()
            artist = artist_elem.text.strip()
            album_link = album_link_elem["href"]
            cover_image = cover_image_elem["src"]
            release_date = release_date_elem.text.strip().lower()

            # Clean album_link
            parsed = urlparse(album_link)
            album_link = parsed._replace(query="", fragment="").geturl()

            # Parse date
            pub_date = self._parse_date(release_date)

            # Process HTML for description
            description = self._process_html(item)

            return FeedItem(
                title=f"{title} by {artist}",
                link=album_link,
                author=artist,
                description=description,
                pub_date=pub_date,
                guid=album_link,
                enclosure_url=cover_image,
            )
        except AttributeError, TypeError:
            return None

    def _parse_date(self, release_date: str) -> datetime:
        now = datetime.now(tz=self.timezone)

        if hours_match := re.match(r"^(\d+)\s+hours?\s+ago$", release_date):
            hours = int(hours_match.group(1))
            return now - timedelta(hours=hours)

        if minutes_match := re.match(r"^(\d+)\s+minutes?\s+ago$", release_date):
            minutes = int(minutes_match.group(1))
            return now - timedelta(minutes=minutes)

        if release_date == "yesterday":
            return now - timedelta(days=1)

        try:
            return datetime.strptime(release_date, "%b %d, %Y").replace(tzinfo=self.timezone)
        except ValueError:
            return now

    def _process_html(self, item: BeautifulSoup) -> str:
        item_copy = BeautifulSoup(str(item), "html.parser")

        remove_elements = [
            ("div", "tralbum-owners"),
            ("div", "story-sidebar"),
            ("div", "tralbum-wrapper-collect-controls"),
            ("span", "track_play_time"),
        ]

        for div_type, div_class in remove_elements:
            element = item_copy.find(div_type, class_=div_class)
            if element:
                element.decompose()

        return f'<div class="collection-item-container">{item_copy}</div>'
