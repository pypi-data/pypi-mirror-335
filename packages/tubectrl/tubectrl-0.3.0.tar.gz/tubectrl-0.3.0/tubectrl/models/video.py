from typing import Optional

from pydantic import BaseModel, Field

from .file_details import FileDetails
from .livestreaming_details import LiveStreamingDetails
from .localizations import Localizations
from .paid_product_placement_details import PaidProductPlacementDetails
from .player import Player
from .processing_details import ProcessingDetails
from .recording_details import RecordingDetails
from .statistics import Statistics
from .suggestions import Suggestions
from .topic_details import TopicDetails
from .video_snippet import VideoSnippet
from .video_status import VideoStatus


class Video(BaseModel):
    kind: Optional[str] = Field(default=None)
    etag: Optional[str] = Field(default=None)
    id: Optional[str] = Field(default=None)
    snippet: Optional[VideoSnippet] = Field(default=None)
    status: Optional[VideoStatus] = Field(default=None)
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
