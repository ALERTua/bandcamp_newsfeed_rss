# Extending Bandcamp Newsfeed RSS

This document describes how to add new feed sources to the application.

## Architecture Overview

The project uses a modular architecture with:

- **Sources** (`sources/`) — Implement data fetching from different providers
- **Routers** (`routers/`) — Define API endpoints for each source
- **Registry** (`sources/registry.py`) — Auto-discovers available sources

## Adding a New Feed Source

### Step 1: Create the Source Class

Create a new file in `sources/` (e.g., `sources/async_api.py`):

```python
"""Bandcamp AsyncAPI feed source."""
from ..sources.registry import register_source
from ..sources.protocol import FeedItem
from .protocol import FeedSource


@register_source("my_source")
class MyBandcampSource(FeedSource):
    """Description of your source."""

    def __init__(self, token: str | None = None):
        self._token = token
        self._url = "https://bandcamp.com/api/..."

    @property
    def feed_url(self) -> str:
        return self._url

    @property
    def feed_title(self) -> str:
        return "My Bandcamp Feed"

    async def fetch_items(self) -> list[FeedItem]:
        # Implement fetching logic
        ...

    async def close(self) -> None:
        # Cleanup if needed
        ...
```

### Step 2: Register the Router

Add the router in `routers/__init__.py`:

```python
from .scraping import create_feed_router
from ..sources import MyBandcampSource  # Import your new source


def create_all_routers():
    """Create all feed routers."""
    return [
        create_feed_router(BandcampScrapingSource, prefix=""),
        create_feed_router(MyBandcampSource, prefix="/my-source"),
    ]
```

Or add it directly in `app.py`:

```python
from .routers import create_feed_router
from .sources import MyBandcampSource

def create_feed_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    # Scraping feed
    app.include_router(
        create_feed_router(BandcampScrapingSource, prefix="")
    )

    # New source
    app.include_router(
        create_feed_router(MyBandcampSource, prefix="/my-source")
    )

    return app
```

### Step 3: Use the New Endpoint

Your new source will be available at:
- `GET /my-source/rss`
- `GET /my-source/atom`

## Available Sources

| Name | Endpoint | Description |
|------|----------|-------------|
| `scraping` | `/rss`, `/atom` | Web scraping of Bandcamp feed |

## Registry

The registry (`sources/registry.py`) provides:

- `@register_source(name)` — Decorator to register a source
- `FEED_SOURCES` — Dict of all registered sources
- `get_source_class(name)` — Get source class by name

This allows dynamic source discovery if needed.
