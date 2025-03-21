from datetime import datetime
from enum import Enum, auto
from typing import Optional

from pydantic import BaseModel, Field

from .request_filter import Filter
from .request_optional_parameters import OptionalParameters
from .request_part import Part


class VideoPart(Part):
    part: list[str] = Field(
        default=[
            "contentDetails",
            "id",
            "liveStreamingDetails",
            "localizations",
            "player",
            "recordingDetails",
            "snippet",
            "statistics",
            "status",
            "topicDetails",
        ]
    )


class VideoFilter(Filter):
    chart: Optional[str] = ""
    id: Optional[list[str]] = Field(default_factory=list)
    myRating: Optional[str] = ""


class VideoOptionalParameters(OptionalParameters):
    h1: Optional[str] = ""
    maxHeight: Optional[int] = None
    maxResults: Optional[int] = None
    maxWidth: Optional[int] = None
    onBehalfOfContentOwner: Optional[str] = ""
    pageToken: Optional[str] = ""
    regionCode: Optional[str] = ""
    videoCategoryId: Optional[str] = ""
