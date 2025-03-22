from typing import Any, Optional

from ...models import (
    PlaylistItem,
    PlaylistItemContentDetails,
    PlaylistItemSnippet,
    PlaylistItemStatus,
    ResourceId,
)
from ..parsers import parse_localized, parse_thumbnail


def parse_resource_id(resource_id_data: dict[str, Any]) -> ResourceId:
    resource_id: ResourceId = ResourceId()
    if resource_id_data.get("kind"):
        resource_id.kind = resource_id_data["kind"]
    if resource_id_data.get("videoId"):
        resource_id.videoId = resource_id_data["videoId"]
    return resource_id


def parse_snippet(snippet_data: dict[str, Any]) -> PlaylistItemSnippet:
    snippet: PlaylistItemSnippet = PlaylistItemSnippet()
    if snippet_data.get("publishedAt"):
        snippet.publishedAt = snippet_data["publishedAt"]
    if snippet_data.get("channelId"):
        snippet.channelId = snippet_data["channelId"]
    if snippet_data.get("title"):
        snippet.title = snippet_data["title"]
    if snippet_data.get("description"):
        snippet.description = snippet_data["description"]
    if snippet_data.get("thumbnails"):
        snippet.thumbnails = [
            parse_thumbnail(resolution, details)
            for resolution, details in snippet_data["thumbnails"].items()
        ]
    if snippet_data.get("channelTitle"):
        snippet.channelTitle = snippet_data["channelTitle"]
    if snippet_data.get("videoOwnerChannelTitle"):
        snippet.videoOwnerChannelTitle = snippet_data["videoOwnerChannelTitle"]
    if snippet_data.get("videoOwnerChannelId"):
        snippet.videoOwnerChannelId = snippet_data["videoOwnerChannelId"]
    if snippet_data.get("playlistId"):
        snippet.playlistId = snippet_data["playlistId"]
    if snippet_data.get("position"):
        snippet.position = snippet_data["position"]
    if snippet_data.get("resourceId"):
        snippet.resourceId = parse_resource_id(snippet_data["resourceId"])
    return snippet


def parse_status(status_data: dict[str, Any]) -> PlaylistItemStatus:
    status: PlaylistItemStatus = PlaylistItemStatus()
    if status_data.get("privacyStatus"):
        status.privacyStatus = status_data["privacyStatus"]
    return status


def parse_content_details(
    content_details_data: dict[str, Any],
) -> PlaylistItemContentDetails:
    content_detail: PlaylistItemContentDetails = PlaylistItemContentDetails()
    if content_details_data.get("videoId"):
        content_detail.videoId = content_details_data["videoId"]
    if content_details_data.get("note"):
        content_detail.note = content_details_data["note"]
    if content_details_data.get("videoPublishedAt"):
        content_detail.videoPublishedAt = content_details_data["videoPublishedAt"]
    return content_detail


class PlaylistItemParser:
    def __init__(
        self, playlist_item_result: dict, playlist_item: PlaylistItem = PlaylistItem()
    ):
        self.playlist_item_result = playlist_item_result
        self.playlist_item = playlist_item

    def parse_kind(self) -> PlaylistItemStatus:
        if "kind" in self.playlist_item_result:
            self.playlist_item.kind = self.playlist_item_result["kind"]
        return self.playlist_item

    def parse_etag(self) -> PlaylistItem:
        if "etag" in self.playlist_item_result:
            self.playlist_item.etag = self.playlist_item_result["etag"]
        return self.playlist_item

    def parse_id(self) -> PlaylistItem:
        if "id" in self.playlist_item_result:
            self.playlist_item.id = self.playlist_item_result["id"]
        return self.playlist_item

    def parse_snippet(self) -> PlaylistItem:
        if "snippet" in self.playlist_item_result:
            self.playlist_item.snippet = parse_snippet(
                self.playlist_item_result["snippet"]
            )
        return self.playlist_item

    def parse_status(self) -> PlaylistItem:
        if "status" in self.playlist_item_result:
            self.playlist_item.status = parse_status(
                self.playlist_item_result["status"]
            )
        return self.playlist_item

    def parse_content_details(self) -> PlaylistItem:
        if "contentDetails" in self.playlist_item_result:
            self.playlist_item.contentDetails = parse_content_details(
                self.playlist_item_result["contentDetails"]
            )
        return self.playlist_item


def parse_playlist_item(playlist_item_result: dict) -> PlaylistItem:
    playlist_item = PlaylistItem()
    playlist_item_parser = PlaylistItemParser(playlist_item_result, playlist_item)
    playlist_item_parser.parse_kind()
    playlist_item_parser.parse_id()
    playlist_item_parser.parse_etag()
    playlist_item_parser.parse_snippet()
    playlist_item_parser.parse_status()
    playlist_item_parser.parse_content_details()
    return playlist_item


def parse_playlist_items_list(playlist_item_result: list[dict]) -> list[PlaylistItem]:
    playlist_items: list[PlaylistItem] = list(
        map(parse_playlist_item, playlist_item_result)
    )
    return playlist_items
