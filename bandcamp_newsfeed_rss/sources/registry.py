"""Feed source registry."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bandcamp_newsfeed_rss.sources.protocol import FeedSource


# Registry of available feed sources
FEED_SOURCES: dict[str, type[FeedSource]] = {}


def register_source(name: str):
    """
    Register a feed source.

    Usage:
        @register_source("my_source")
        class MySource:
            ...
    """

    def decorator(cls: type[FeedSource]):
        FEED_SOURCES[name] = cls
        return cls

    return decorator


def get_source_class(name: str) -> type[FeedSource] | None:
    """Get source class by name."""
    return FEED_SOURCES.get(name)


__all__ = ["FEED_SOURCES", "get_source_class", "register_source"]
