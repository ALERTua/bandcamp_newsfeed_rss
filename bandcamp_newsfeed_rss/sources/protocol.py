"""Feed source abstractions."""

from typing import TYPE_CHECKING, Protocol


if TYPE_CHECKING:
    from ..models import FeedItem


class FeedSource(Protocol):
    """Protocol for feed sources."""

    @property
    def feed_url(self) -> str:
        """Return the URL of the feed."""
        ...

    @property
    def feed_title(self) -> str:
        """Return the title of the feed."""
        ...

    async def fetch_items(self) -> list[FeedItem]:
        """Fetch items from the feed source."""
        ...

    async def close(self) -> None:
        """Close the feed source."""
        ...
