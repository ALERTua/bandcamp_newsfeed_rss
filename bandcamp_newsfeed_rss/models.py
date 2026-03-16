"""Pydantic models."""

from pydantic import BaseModel


class HealthCheck(BaseModel):
    """Response model for health check endpoint."""

    status: str = "OK"
