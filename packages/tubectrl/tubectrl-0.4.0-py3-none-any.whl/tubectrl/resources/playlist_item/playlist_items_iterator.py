from typing import Any

from ...models.playlist_item import PlaylistItem
from ...schemas.playlist_item import (
    PlaylistItemFilter,
    PlaylistItemOptionalParameters,
    PlaylistItemPart,
)
from ...schemas.youtube_request import YouTubeRequest
from ..utils import create_request_dict
from .parsers import parse_playlist_items_list


class PlaylistItemIterator:
    def __init__(self, youtube_client: Any, playlist_id: str, max_results: int = 25):
        self.youtube_client = youtube_client
        self.request_schema: YouTubeRequest = self._create_request_schema(
            playlist_id, max_results
        )
        self.next_page_token: str = ""
        self.done: bool = False

    def _create_request_schema(
        self, playlist_id: str, max_results: int
    ) -> YouTubeRequest:
        part: PlaylistItemPart = PlaylistItemPart()
        request_filter: PlaylistItemFilter = PlaylistItemFilter(playlistId=playlist_id)
        optional_params: PlaylistItemOptionalParameters = (
            PlaylistItemOptionalParameters(maxResults=max_results)
        )
        request_schema: YouTubeRequest = YouTubeRequest(
            part=part,
            optional_parameters=optional_params,
            filter=request_filter,
        )
        return request_schema

    def __iter__(self):
        return self

    def __next__(self) -> list[PlaylistItem]:
        if self.done:
            raise StopIteration()
        self.request_schema.optional_parameters.pageToken = self.next_page_token
        request_dict: dict = create_request_dict(self.request_schema)
        find_playlist_items_request: dict = self.youtube_client.playlistItems().list(
            **request_dict
        )
        find_playlist_items_resp: dict = find_playlist_items_request.execute()
        self.next_page_token = find_playlist_items_resp.get("nextPageToken")
        if not self.next_page_token:
            self.done = True
        playlist_items = parse_playlist_items_list(
            playlist_item_result=find_playlist_items_resp["items"]
        )
        return playlist_items
