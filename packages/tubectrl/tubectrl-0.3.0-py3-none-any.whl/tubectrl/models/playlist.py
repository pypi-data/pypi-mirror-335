from typing import Optional

from pydantic import BaseModel, Field

from .playlist_content_details import PlaylistContentDetails
from .playlist_player import PlaylistPlayer
from .playlist_snippet import PlaylistSnippet
from .playlist_status import PlaylistStatus
from .thumbnail import Thumbnail


class Playlist(BaseModel):
    kind: Optional[str] = Field(default=None)
    etag: Optional[str] = Field(default=None)
    id: Optional[str] = Field(default=None)
    snippet: Optional[PlaylistSnippet] = Field(default=None)
    thumbnails: Optional[list[Thumbnail]] = Field(default=None)
    status: Optional[PlaylistStatus] = Field(default=None)
    player: Optional[PlaylistPlayer] = Field(default=None)
    contentDetails: Optional[PlaylistContentDetails] = Field(default=None)
