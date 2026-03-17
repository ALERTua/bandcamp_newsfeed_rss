"""Feed source factory for creating source instances."""

from contextlib import asynccontextmanager

from fastapi import HTTPException

from ..config import BANDCAMP_USERNAME, IDENTITY, TIMEZONE
from ..models import SourceType
from .bandcamp import BandcampScrapingSource
from .bandcamp_api import BandcampAPISource

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


# Mapping for easy extension
SOURCE_CLASSES: dict[str, type] = {
    SourceType.SCRAPING.value: BandcampScrapingSource,
    SourceType.API.value: BandcampAPISource,
}


@asynccontextmanager
async def get_feed_source(
    source_type: str = SourceType.SCRAPING.value,
) -> AsyncGenerator[BandcampScrapingSource | BandcampAPISource, Any]:
    """
    FastAPI dependency for creating feed sources.

    This dependency creates a source instance per request and ensures
    proper cleanup by calling close() in the finally block.

    Args:
        source_type: The type of source to create. Defaults to "scraping".

    Returns:
        A FeedSource instance.

    Raises:
        HTTPException: If the source_type is not recognized.

    """
    source_class = SOURCE_CLASSES.get(source_type)

    if source_class is None:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid source_type: '{source_type}'. Available: {', '.join(SourceType.values())}",
        )

    source = source_class(
        bandcamp_username=BANDCAMP_USERNAME,
        identity_token=IDENTITY,
        timezone=TIMEZONE,
    )

    yield source
    await source.close()
