from typing import Optional

from pydantic import Field

from .status import Status


class PlaylistItemStatus(Status):
    privacyStatus: Optional[str] = Field(default=None)
