"""RSS/Atom feed generator."""
import asyncio
import logging

from feedgen.feed import FeedGenerator

from bandcamp_newsfeed_rss.sources import FeedItem, FeedSource

logger = logging.getLogger(__name__)


class RSSGenerator:
    """Generates RSS/Atom feeds from FeedSource."""

    def __init__(self, source: FeedSource):
        self.source = source

    def generate(self, atom: bool = False) -> bytes:  # noqa: FBT001
        """Generate RSS or Atom feed."""
        logger.info(f"Generating {'atom' if atom else 'rss'} feed from {self.source.feed_url}")

        items = asyncio.run(self.source.fetch_items())

        fg = FeedGenerator()
        fg.title(self.source.feed_title)
        fg.id(self.source.feed_url)
        fg.link(href=self.source.feed_url)
        fg.description(f"RSS feed of {self.source.feed_title}")

        for item in items:
            self._add_entry(fg, item)

        logger.info(f"Generated feed with {len(items)} items")
        return fg.atom_str(pretty=True) if atom else fg.rss_str(pretty=True)

    def _add_entry(self, fg: FeedGenerator, item: FeedItem) -> None:
        entry = fg.add_entry()
        entry.guid(item.guid or item.link, permalink=True)
        entry.title(item.title)
        entry.link(href=item.link)
        entry.author({"name": item.author})
        entry.description(item.description)
        entry.pubDate(item.pub_date)

        if item.enclosure_url:
            entry.enclosure(url=item.enclosure_url, type=item.enclosure_type)
