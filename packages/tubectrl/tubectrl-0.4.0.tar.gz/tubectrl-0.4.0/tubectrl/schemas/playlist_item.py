from typing import Optional

from pydantic import Field

from .request_filter import Filter
from .request_optional_parameters import OptionalParameters
from .request_part import Part


class PlaylistItemFilter(Filter):
    playlistId: Optional[str] = ""
    id: Optional[list[str]] = Field(default_factory=list)


class PlaylistItemOptionalParameters(OptionalParameters):
    maxResults: Optional[int] = None
    onBehalfOfContentOwner: Optional[str] = ""
    videoId: Optional[str] = ""
    pageToken: Optional[str] = ""


class PlaylistItemPart(Part):
    part: list[str] = Field(
        default=[
            "contentDetails",
            "id",
            "snippet",
            "status",
        ]
    )
