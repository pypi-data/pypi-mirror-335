from typing import Optional

from pydantic import BaseModel, Field

from .playlist_content_details import PlaylistContentDetails
from .playlist_item_snippet import PlaylistItemSnippet
from .playlist_item_status import PlaylistItemStatus


class PlaylistItem(BaseModel):
    kind: Optional[str] = Field(default=None)
    etag: Optional[str] = Field(default=None)
    id: Optional[str] = Field(default=None)
    snippet: Optional[PlaylistItemSnippet] = Field(default=None)
    contentDetails: Optional[PlaylistContentDetails] = Field(default=None)
    status: Optional[PlaylistItemStatus] = Field(default=None)
