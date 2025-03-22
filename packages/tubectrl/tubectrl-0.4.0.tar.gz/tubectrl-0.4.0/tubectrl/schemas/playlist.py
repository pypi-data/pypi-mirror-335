from typing import Optional

from pydantic import Field

from .request_filter import Filter
from .request_optional_parameters import OptionalParameters
from .request_part import Part


class PlaylistFilter(Filter):
    channelId: Optional[str] = ""
    id: Optional[list[str]] = Field(default_factory=list)
    mine: Optional[bool] = False


class PlaylistOptionalParameters(OptionalParameters):
    h1: Optional[str] = ""
    maxResults: Optional[int] = None
    onBehalfOfContentOwner: Optional[str] = ""
    onBehalfOfContentOwnerChannel: Optional[str] = ""
    pageToken: Optional[str] = ""


class PlaylistPart(Part):
    part: list[str] = Field(
        default=[
            "contentDetails",
            "id",
            "player",
            "snippet",
            "status",
            "localizations",
        ]
    )
