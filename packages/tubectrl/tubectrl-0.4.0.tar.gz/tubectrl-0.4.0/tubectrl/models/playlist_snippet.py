from typing import Optional

from pydantic import Field

from .localized import Localized
from .snippet import Snippet
from .thumbnail import Thumbnail


class PlaylistSnippet(Snippet):
    publishedAt: Optional[str] = Field(default=None)
    channelId: Optional[str] = Field(default=None)
    title: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    thumbnails: list[Thumbnail] = []
    localized: Optional[Localized] = Field(default=None)
    defaultLanguage: Optional[str] = Field(default=None)
