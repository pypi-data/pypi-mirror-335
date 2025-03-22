from typing import Optional

from pydantic import BaseModel, Field

from .page_info import PageInfo
from .playlist import Playlist


class PlaylistListResponse(BaseModel):
    kind: str
    etag: str
    nextPageToken: str = ""
    prevPageToken: str = ""
    pageInfo: Optional[PageInfo] = None
    items: list[Playlist] = Field(default_factory=list)
