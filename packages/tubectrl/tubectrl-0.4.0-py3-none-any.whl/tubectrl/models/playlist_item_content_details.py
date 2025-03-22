from typing import Optional

from pydantic import Field

from .content_details import ContentDetails


class PlaylistItemContentDetails(ContentDetails):
    videoId: Optional[str] = Field(default=None)
    note: Optional[str] = Field(default=None)
    videoPublishedAt: Optional[str] = Field(default=None)
