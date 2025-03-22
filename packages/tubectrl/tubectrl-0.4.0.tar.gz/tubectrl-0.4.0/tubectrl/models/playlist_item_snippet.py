from typing import Optional

from pydantic import Field

from .localized import Localized
from .resource_id import ResourceId
from .snippet import Snippet
from .thumbnail import Thumbnail


class PlaylistItemSnippet(Snippet):
    publishedAt: Optional[str] = Field(default=None)
    channelId: Optional[str] = Field(default=None)
    title: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    thumbnails: list[Thumbnail] = []
    channelTitle: Optional[str] = Field(default=None)
    videoOwnerChannelTitle: Optional[str] = Field(default=None)
    videoOwnerChannelId: Optional[str] = Field(default=None)
    playlistId: Optional[str] = Field(default=None)
    position: Optional[int] = Field(default=None)
    resourceId: Optional[ResourceId] = Field(default=None)
