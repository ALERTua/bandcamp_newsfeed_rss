"""Pydantic models."""

from enum import StrEnum
from dataclasses import dataclass
from pydantic import BaseModel

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime


class SourceType(StrEnum):
    SCRAPING = "scraping"
    API = "api"

    @classmethod
    def values(cls):
        return [member.value for member in cls]


class HealthCheck(BaseModel):
    """Response model for health check endpoint."""

    status: str = "OK"


@dataclass(frozen=True)
class FeedType:
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
