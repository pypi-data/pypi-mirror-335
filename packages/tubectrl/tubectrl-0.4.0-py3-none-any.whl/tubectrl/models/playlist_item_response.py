from typing import Optional

from pydantic import BaseModel, Field

from .page_info import PageInfo
from .playlist_item import PlaylistItem


class PlaylistItemtResponse(BaseModel):
    kind: str
    etag: str
    nextPageToken: str = ""
    prevPageToken: str = ""
    pageInfo: Optional[PageInfo] = None
    items: list[PlaylistItem] = Field(default_factory=list)
