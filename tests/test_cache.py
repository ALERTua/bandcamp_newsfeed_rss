"""Unit tests for cache."""

import time

from bandcamp_newsfeed_rss import cache


def test_get_cached_returns_none_when_empty(clean_cache) -> None:
    """Test get_cached returns None when cache is empty."""
    result = cache.get_cached("rss")
    assert result is None


def test_get_cached_returns_cached_content(clean_cache) -> None:
    """Test get_cached returns cached content when valid."""
    test_content = b"<rss>test</rss>"
    cache.cache["rss"] = test_content
    cache.cache_timestamp["rss"] = time.time()

    result = cache.get_cached("rss")

    assert result == test_content


def test_get_cached_returns_none_when_expired(clean_cache) -> None:
    """Test get_cached returns None when cache is expired."""
    cache.cache["rss"] = b"<rss>test</rss>"
    cache.cache_timestamp["rss"] = time.time() - 4000  # Expired (default 3600s)

    result = cache.get_cached("rss")

    assert result is None


def test_set_cached(clean_cache) -> None:
    """Test set_cached stores content."""
    test_content = b"<rss>new content</rss>"

    cache.set_cached("rss", test_content)

    assert cache.cache["rss"] == test_content
    assert cache.cache_timestamp["rss"] > 0


def test_get_cached_different_types(clean_cache) -> None:
    """Test cache works for different feed types."""
    rss_content = b"<rss>RSS</rss>"
    atom_content = b"<atom>Atom</atom>"

    cache.set_cached("rss", rss_content)
    cache.set_cached("atom", atom_content)

    assert cache.get_cached("rss") == rss_content
    assert cache.get_cached("atom") == atom_content
