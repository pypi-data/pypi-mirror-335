from typing import Literal

from pydantic import BaseModel

from .content_details import ContentDetails
from .content_rating import ContentRating
from .region_restriction import RegionRestriction
from .video_status import Status


class VideoContentDetails(ContentDetails):
    duration: str
    dimension: str
    definition: Literal["hd", "sd"]
    definition: Literal["false", "true"]
    licensedContent: bool
    regionRestriction: RegionRestriction
    duration: str
    contentRating: ContentRating
    projection: Literal["360", "rectangular"]
    status: Status
