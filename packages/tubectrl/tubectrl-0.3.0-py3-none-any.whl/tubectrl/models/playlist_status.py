from typing import Literal

from pydantic import Field

from .status import Status


class PlaylistStatus(Status):
    privacyStatus: Literal["private", "public", "unlisted"] = Field(default="public")
    podcastStatus: Literal["enabled", "disabled", "unspecified"] = Field(
        default="unspecified"
    )
