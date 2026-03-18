"""RSS/Atom feed generator."""

import logging
from typing import TYPE_CHECKING

from feedgen.feed import FeedGenerator
from .models import FeedType

if TYPE_CHECKING:
    from .models import FeedItem
    from .sources.base import FeedSource

logger = logging.getLogger(__name__)


class RSSGenerator:
    """Generates RSS/Atom feeds from FeedSource."""

    def __init__(self, source: FeedSource, feed_type: str):
        self.source = source
        self.feed_type = feed_type

    async def generate(self) -> bytes:
        """Generate RSS or Atom feed."""
        logger.info(f"Generating {self.feed_type} feed from {self.source.feed_url}")

        items = await self.source.fetch_items()

        fg = FeedGenerator()
        fg.title(self.source.feed_title)
        fg.id(self.source.feed_url)
        fg.link(href=self.source.feed_url)
        if self.source.feed_url:
            fg.link(href=self.source.feed_url, rel="self")
        fg.description(f"RSS feed of {self.source.feed_title}")

        for item in items:
            self._add_entry(fg, item)

        logger.info(f"Generated feed with {len(items)} items")
        match self.feed_type:
            case FeedType.RSS:
                return fg.rss_str(pretty=True)
            case FeedType.ATOM:
                return fg.atom_str(pretty=True)
            case _:
                msg = f"Unknown feed type: {self.feed_type}"
                raise ValueError(msg)

    def _add_entry(self, fg: FeedGenerator, item: FeedItem) -> None:
        entry = fg.add_entry()
        entry.guid(item.guid or item.link, permalink=True)
        entry.title(item.title)
        entry.link(href=item.link)
        entry.author({"name": item.author})
        entry.description(item.description)
        entry.published(item.pub_date)
        entry.updated(item.pub_date)
        for tag in item.tags:
            entry.category(term=tag)

        if item.enclosure_url:
            entry.enclosure(url=item.enclosure_url, type=item.enclosure_type)
