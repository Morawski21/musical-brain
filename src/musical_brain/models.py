"""
Pydantic models for Musical Brain entities.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AlbumType(str, Enum):
    """Album type enumeration."""
    LP = "LP"
    EP = "EP"
    SINGLE = "Single"
    LIVE = "Live"
    COMPILATION = "Compilation"


class Album(BaseModel):
    """Album model."""
    id: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=200)
    album_type: AlbumType
    release_year: Optional[int] = Field(None, ge=1900, le=2030)
    review_score: Optional[float] = Field(None, ge=0.0, le=5.0)
    review_notes: Optional[str] = None
    review_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class Artist(BaseModel):
    """Artist model."""
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=200)
    country: Optional[str] = Field(None, max_length=100)
    formed_year: Optional[int] = Field(None, ge=1800, le=2030)
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class Genre(BaseModel):
    """Genre model."""
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)