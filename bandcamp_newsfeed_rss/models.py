"""Models."""

from enum import StrEnum
from dataclasses import dataclass, field
from pydantic import BaseModel

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime


class StrEnumBase(StrEnum):
    """Base class for StrEnums."""

    @classmethod
    def values(cls):
        return [member.value for member in cls]


class SourceType(StrEnumBase):
    SCRAPING = "scraping"
    API = "api"


class FeedType(StrEnumBase):
    """Feed type."""

    RSS = "rss"
    ATOM = "atom"


@dataclass(frozen=True)
class FeedItem:
    """Represents a single item in a feed."""

    title: str
    link: str
    author: str
    description: str
    pub_date: datetime
    guid: str | None = None
    enclosure_url: str | None = None
    enclosure_type: str = "image/jpeg"
    tags: list[str] = field(default_factory=list)


class HealthCheck(BaseModel):
    """Response model for health check endpoint."""

    status: str = "OK"
