"""Feed sources."""

from .bandcamp import BandcampScrapingSource
from .protocol import FeedItem, FeedSource
from .registry import FEED_SOURCES, get_source_class, register_source

__all__ = [
    "FEED_SOURCES",
    "BandcampScrapingSource",
    "FeedItem",
    "FeedSource",
    "get_source_class",
    "register_source",
]
