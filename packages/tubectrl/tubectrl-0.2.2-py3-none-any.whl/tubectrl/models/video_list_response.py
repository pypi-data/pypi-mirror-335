from typing import Optional

from pydantic import BaseModel, Field

from .page_info import PageInfo
from .video import Video


class VideoListResponse(BaseModel):
    kind: str
    etag: str
    nextPageToken: str = ""
    prevPageToken: str = ""
    pageInfo: Optional[PageInfo] = None
    items: list[Video] = Field(default_factory=list)
