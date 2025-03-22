from typing import Any

from ...models.playlist import Playlist
from ...models.playlist_list_response import PlaylistListResponse
from ...schemas.playlist import PlaylistFilter, PlaylistOptionalParameters, PlaylistPart
from ...schemas.youtube_request import YouTubeRequest
from ..utils import create_request_dict
from .parsers import parse_playlist_list


class PlaylistIterator:
    def __init__(self, youtube_client: Any, channel_id: str, max_results: int = 25):
        self.youtube_client = youtube_client
        self.request_schema: YouTubeRequest = self._create_request_schema(
            channel_id, max_results
        )
        self.next_page_token: str = ""
        self.done: bool = False

    def _create_request_schema(
        self, channel_id: str, max_results: int
    ) -> YouTubeRequest:
        part: PlaylistPart = PlaylistPart()
        request_filter: PlaylistFilter = PlaylistFilter(channelId=channel_id)
        optional_params: PlaylistOptionalParameters = PlaylistOptionalParameters(
            maxResults=max_results
        )
        request_schema: YouTubeRequest = YouTubeRequest(
            part=part,
            optional_parameters=optional_params,
            filter=request_filter,
        )
        return request_schema

    def __iter__(self):
        return self

    def __next__(self) -> list[Playlist]:
        if self.done:
            raise StopIteration()
        self.request_schema.optional_parameters.pageToken = self.next_page_token
        request_dict: dict = create_request_dict(self.request_schema)
        find_channel_playlist_request: dict = self.youtube_client.playlists().list(
            **request_dict
        )
        find_channel_resp: dict = find_channel_playlist_request.execute()
        self.next_page_token = find_channel_resp.get("nextPageToken")
        if not self.next_page_token:
            self.done = True
        playlists = parse_playlist_list(playlist_result=find_channel_resp["items"])
        return playlists
