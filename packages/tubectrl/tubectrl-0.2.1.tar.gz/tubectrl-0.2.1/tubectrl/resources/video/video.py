from typing import Any

from ...exceptions import VideoNotFoundException
from ...models import Video
from ...schemas import VideoFilter, VideoOptionalParameters, VideoPart, YouTubeRequest
from ..utils import create_request_dict
from .parsers import parse_video, parse_video_list


class YouTubeVideoResource:
    def __init__(self, youtube_client: Any):
        self.youtube_client = youtube_client

    def find_video_by_id(self, video_id: str) -> Video:
        request_filter: VideoFilter = VideoFilter(id=[video_id])
        request_part: VideoPart = VideoPart()
        request_optional_params: VideoOptionalParameters = VideoOptionalParameters()
        youtube_request: YouTubeRequest = YouTubeRequest(
            part=request_part,
            filter=request_filter,
            optional_parameters=request_optional_params,
        )
        request_dict = create_request_dict(youtube_request)
        find_video_request: dict = self.youtube_client.videos().list(**request_dict)
        find_video_result: dict[str, Any] = find_video_request.execute()
        if not find_video_result["items"]:
            raise VideoNotFoundException("No such video exists")
        video: Video = parse_video(find_video_result["items"][0])
        return video

    def find_videos_by_ids(self, video_ids: str) -> list[Video]:
        request_filter: VideoFilter = VideoFilter(id=video_ids)
        request_part: VideoPart = VideoPart()
        request_optional_params: VideoOptionalParameters = VideoOptionalParameters()
        youtube_request: YouTubeRequest = YouTubeRequest(
            part=request_part,
            filter=request_filter,
            optional_parameters=request_optional_params,
        )
        request_dict = create_request_dict(youtube_request)
        find_video_request: dict = self.youtube_client.videos().list(**request_dict)
        find_video_result: dict[str, Any] = find_video_request.execute()
        if not find_video_result["items"]:
            raise VideoNotFoundException("No such videos exist")
        videos = parse_video_list(find_video_result["items"])
        return videos
