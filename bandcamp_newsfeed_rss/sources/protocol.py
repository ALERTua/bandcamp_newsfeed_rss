"""Feed source abstractions."""

from datetime import datetime
from typing import Protocol, Any


class FeedItem:
    """Represents a single item in a feed."""

    def __init__(  # noqa: PLR0913
        self,
        title: str,
        link: str,
        author: str,
        description: str,
        pub_date: datetime,
        guid: str | None = None,
        enclosure_url: str | None = None,
        enclosure_type: str = "image/jpeg",
    ):
        self.title = title
        self.link = link
        self.author = author
        self.description = description
        self.pub_date = pub_date
        self.guid = guid
        self.enclosure_url = enclosure_url
        self.enclosure_type = enclosure_type

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "link": self.link,
            "author": self.author,
            "description": self.description,
            "pub_date": self.pub_date,
            "guid": self.guid,
            "enclosure_url": self.enclosure_url,
            "enclosure_type": self.enclosure_type,
        }


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
