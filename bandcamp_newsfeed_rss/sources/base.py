"""Feed source abstractions."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from ..models import FeedItem


class FeedSource(ABC):
    """Abstract base class for feed sources."""

    @property
    @abstractmethod
    def feed_url(self) -> str:
        """Return the URL of the feed."""

    @property
    @abstractmethod
    def feed_title(self) -> str:
        """Return the title of the feed."""

    @abstractmethod
    async def fetch_items(self) -> list[FeedItem]:
        """Fetch items from the feed source."""

    @abstractmethod
    async def close(self) -> None:
        """Close the feed source."""

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()
