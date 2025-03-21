from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

from .localized import Localized
from .thumbnail import Thumbnail


class Snippet(BaseModel):
    title: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    thumbnails: list[Thumbnail] = []
    publishedAt: Optional[str] = Field(default=None)
    channelId: Optional[str] = Field(default=None)
    channelTitle: Optional[str] = Field(default=None)
    categoryId: Optional[str] = Field(default=None)
    categoryId: Optional[str] = Field(default=None)
    localized: Optional[Localized] = Field(default=None)
    defaultAudioLanguage: Optional[str] = Field(default=None)
    defaultLanguage: Optional[str] = Field(default=None)
    tags: list[str] = []
