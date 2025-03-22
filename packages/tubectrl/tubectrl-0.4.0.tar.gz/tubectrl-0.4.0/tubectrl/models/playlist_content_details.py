from typing import Optional

from pydantic import Field

from .content_details import ContentDetails


class PlaylistContentDetails(ContentDetails):
    itemCount: Optional[int] = Field(default=None)
