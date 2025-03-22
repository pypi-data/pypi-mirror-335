from typing import Any

from ...models import (
    FileDetails,
    LiveStreamingDetails,
    Localizations,
    Localized,
    PaidProductPlacementDetails,
    Player,
    ProcessingDetails,
    RecordingDetails,
    Statistics,
    Suggestions,
    Thumbnail,
    TopicDetails,
    Video,
    VideoSnippet,
    VideoStatus,
)
from ..parsers import parse_localized, parse_thumbnail


def parse_snippet(snippet_data: dict[str, Any]) -> VideoSnippet:
    snippet: VideoSnippet = VideoSnippet()
    if snippet_data.get("title"):
        snippet.title = snippet_data["title"]
    if snippet_data.get("description"):
        snippet.description = snippet_data["description"]
    if snippet_data.get("thumbnails"):
        snippet.thumbnails = [
            parse_thumbnail(resolution, details)
            for resolution, details in snippet_data["thumbnails"].items()
        ]
    if snippet_data.get("publishedAt"):
        snippet.publishedAt = snippet_data["publishedAt"]
    if snippet_data.get("channelId"):
        snippet.channelId = snippet_data["channelId"]
    if snippet_data.get("channelTitle"):
        snippet.channelTitle = snippet_data["channelTitle"]
    if snippet_data.get("categoryId"):
        snippet.categoryId = snippet_data["categoryId"]
    if snippet_data.get("localized"):
        snippet.localized = parse_localized(snippet_data["localized"])
    if snippet_data.get("defaultAudioLanguage"):
        snippet.defaultAudioLanguage = snippet_data["defaultAudioLanguage"]
    if snippet_data.get("defaultLanguage"):
        snippet.defaultLanguage = snippet_data["defaultLanguage"]
    if snippet_data.get("tags"):
        snippet.tags = snippet_data["tags"]
    return snippet


def parse_status(status_data: dict[str, int]) -> VideoStatus:
    pass


def parse_statistics(statistics_data: dict[str, int]) -> Statistics:
    statistics: Statistics = Statistics()
    if statistics_data.get("viewCount"):
        statistics.viewCount = statistics_data["viewCount"]
    if statistics_data.get("likeCount"):
        statistics.likeCount = statistics_data["likeCount"]
    if statistics_data.get("dislikeCount"):
        statistics.dislikeCount = statistics_data["dislikeCount"]
    if statistics_data.get("favoriteCount"):
        statistics.favoriteCount = statistics_data["favoriteCount"]
    if statistics_data.get("commentCount"):
        statistics.commentCount = statistics_data["commentCount"]
    return statistics


def parse_paid_product_details(
    statistics_data: dict[str, int],
) -> PaidProductPlacementDetails:
    pass


def parse_player(statistics_data: dict[str, int]) -> Player:
    pass


def parse_topic_details(topic_details_data: dict[str, int]) -> TopicDetails:
    pass


def parse_recording_details(recording_data: dict[str, int]) -> RecordingDetails:
    pass


def parse_file_details(file_data: dict[str, int]) -> FileDetails:
    pass


def parse_processing_details(processing_data: dict[str, int]) -> ProcessingDetails:
    pass


def parse_suggestions(suggestions_data: dict[str, int]) -> Suggestions:
    pass


def parse_livestreaming_details(
    livestreaming_data: dict[str, int],
) -> LiveStreamingDetails:
    pass


def parse_localizations(localizations_data: dict[str, int]) -> Localizations:
    pass


class VideoParser:
    def __init__(self, video_result: dict, video: Video = Video()):
        self.video_result = video_result
        self.video = video

    def parse_kind(self) -> Video:
        if "kind" in self.video_result:
            self.video.kind = self.video_result["kind"]
        return self.video

    def parse_etag(self) -> Video:
        if "etag" in self.video_result:
            self.video.etag = self.video_result["etag"]
        return self.video

    def parse_id(self) -> Video:
        if "id" in self.video_result:
            self.video.id = self.video_result["id"]
        return self.video

    def parse_snippet(self) -> Video:
        if "snippet" in self.video_result:
            self.video.snippet = parse_snippet(self.video_result["snippet"])
        return self.video

    def parse_status(self) -> Video:
        if "status" in self.video_result:
            self.video.status = parse_status(self.video_result["status"])
        return self.video

    def parse_statistics(self) -> Video:
        if "statistics" in self.video_result:
            self.video.statistics = parse_statistics(self.video_result["statistics"])
        return self.video

    def parse_paid_product_placement_details(self) -> Video:
        if "paidProductPlacementDetails" in self.video_result:
            self.video.paidProductPlacementDetails = parse_paid_product_details(
                self.video_result["paidProductPlacementDetails"]
            )
        return self.video

    def parse_player(self) -> Video:
        if "player" in self.video_result:
            self.video.player = parse_player(self.video_result["player"])
        return self.video

    def parse_topic_details(self) -> Video:
        if "topicDetails" in self.video_result:
            self.video.topicDetails = parse_topic_details(
                self.video_result["topicDetails"]
            )
        return self.video

    def parse_recording_details(self) -> Video:
        if "recordingDetails" in self.video_result:
            self.video.recordingDetails = parse_recording_details(
                self.video_result["recordingDetails"]
            )
        return self.video

    def parse_file_details(self) -> Video:
        if "fileDetails" in self.video_result:
            self.video.fileDetails = parse_file_details(
                self.video_result["fileDetails"]
            )
        return self.video

    def parse_processing_details(self) -> Video:
        if "processingDetails" in self.video_result:
            self.video.processingDetails = parse_processing_details(
                self.video_result["processingDetails"]
            )
        return self.video

    def parse_suggestions(self) -> Video:
        if "suggestions" in self.video_result:
            self.video.suggestions = parse_suggestions(self.video_result["suggestions"])
        return self.video


def parse_video(video_result: dict) -> Video:
    video = Video()
    video_parser = VideoParser(video_result, video)
    video_parser.parse_kind()
    video_parser.parse_id()
    video_parser.parse_etag()
    video_parser.parse_snippet()
    video_parser.parse_status()
    video_parser.parse_statistics()
    video_parser.parse_paid_product_placement_details()
    video_parser.parse_player()
    video_parser.parse_topic_details()
    video_parser.parse_recording_details()
    video_parser.parse_file_details()
    video_parser.parse_processing_details()
    video_parser.parse_suggestions()
    return video


def parse_video_list(video_result: list[dict]) -> list[Video]:
    videos: list[Video] = list(map(parse_video, video_result))
    return videos
