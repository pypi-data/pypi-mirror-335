from typing import Optional

from pydantic import BaseModel, Field

from .file_details import FileDetails
from .livestreaming_details import LiveStreamingDetails
from .localizations import Localizations
from .paid_product_placement_details import PaidProductPlacementDetails
from .player import Player
from .processing_details import ProcessingDetails
from .recording_details import RecordingDetails
from .snippet import Snippet
from .statistics import Statistics
from .status import Status
from .suggestions import Suggestions
from .topic_details import TopicDetails


class Video(BaseModel):
    kind: Optional[str] = Field(default=None)
    etag: Optional[str] = Field(default=None)
    id: Optional[str] = Field(default=None)
    snippet: Optional[Snippet] = Field(default=None)
    status: Optional[Status] = Field(default=None)
    statistics: Optional[Statistics] = Field(default=None)
    paidProductPlacementDetails: Optional[PaidProductPlacementDetails] = Field(
        default=None
    )
    player: Optional[Player] = Field(default=None)
    topicDetails: Optional[TopicDetails] = Field(default=None)
    recordingDetails: Optional[RecordingDetails] = Field(default=None)
    fileDetails: Optional[FileDetails] = Field(default=None)
    processingDetails: Optional[ProcessingDetails] = Field(default=None)
    suggestions: Optional[Suggestions] = Field(default=None)
    liveStreamingDetails: Optional[LiveStreamingDetails] = Field(default=None)
    localizations: Optional[Localizations] = Field(default=None)
