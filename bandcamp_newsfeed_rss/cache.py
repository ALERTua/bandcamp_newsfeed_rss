"""In-memory feed cache."""

import time

from .config import CACHE_DURATION_SECONDS, logger

# Cache storage
cache: dict[str, bytes | None] = {}
cache_timestamp: dict[str, float] = {}


def get_cached(feed_type: str) -> bytes | None:
    """Get cached feed if still valid."""
    current_time = time.time()
    if cache.get(feed_type) and (current_time - cache_timestamp.get(feed_type, 0)) < CACHE_DURATION_SECONDS:
        logger.info(f"Returning cached {feed_type} feed")
        return cache[feed_type]
    return None


def set_cached(feed_type: str, content: bytes) -> None:
    """Cache feed content."""
    cache[feed_type] = content
    cache_timestamp[feed_type] = time.time()
    logger.info(f"Cached new {feed_type} feed")


def clear_cache() -> None:
    """Remove all entries from the cache."""
    cache.clear()
    cache_timestamp.clear()
