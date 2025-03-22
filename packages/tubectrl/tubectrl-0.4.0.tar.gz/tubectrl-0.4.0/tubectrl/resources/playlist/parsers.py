from typing import Any

from ...models.playlist import (
    Playlist,
    PlaylistContentDetails,
    PlaylistPlayer,
    PlaylistSnippet,
    PlaylistStatus,
)
from ..parsers import parse_localized, parse_thumbnail


def parse_snippet(snippet_data: dict[str, Any]) -> PlaylistSnippet:
    snippet: PlaylistSnippet = PlaylistSnippet()
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
    if snippet_data.get("localized"):
        snippet.localized = parse_localized(snippet_data["localized"])
    if snippet_data.get("defaultLanguage"):
        snippet.defaultLanguage = snippet_data["defaultLanguage"]
    return snippet


def parse_status(status_data: dict[str, Any]) -> PlaylistStatus:
    status: PlaylistStatus = PlaylistStatus()
    if status_data.get("privacyStatus"):
        status.privacyStatus = status_data["privacyStatus"]
    if status_data.get("podcastStatus"):
        status.podcastStatus = status_data["podcastStatus"]
    return status


def parse_player(playlist_player_data: dict[str, Any]) -> PlaylistPlayer:
    player: PlaylistPlayer = PlaylistPlayer()
    if playlist_player_data.get("embedHtml"):
        player.embedHtml = playlist_player_data["embedHtml"]
    return player


def parse_content_details(
    content_details_data: dict[str, Any],
) -> PlaylistContentDetails:
    content_detail: PlaylistContentDetails = PlaylistContentDetails()
    if content_details_data.get("itemCount"):
        content_detail.itemCount = content_details_data["itemCount"]
    return content_detail


class PlaylistParser:
    def __init__(self, playlist_result: dict, playlist: Playlist = Playlist()):
        self.playlist_result = playlist_result
        self.playlist = playlist

    def parse_kind(self) -> Playlist:
        if "kind" in self.playlist_result:
            self.playlist.kind = self.playlist_result["kind"]
        return self.playlist

    def parse_etag(self) -> Playlist:
        if "etag" in self.playlist_result:
            self.playlist.etag = self.playlist_result["etag"]
        return self.playlist

    def parse_id(self) -> Playlist:
        if "id" in self.playlist_result:
            self.playlist.id = self.playlist_result["id"]
        return self.playlist

    def parse_snippet(self) -> Playlist:
        if "snippet" in self.playlist_result:
            self.playlist.snippet = parse_snippet(self.playlist_result["snippet"])
        return self.playlist

    def parse_status(self) -> Playlist:
        if "status" in self.playlist_result:
            self.playlist.status = parse_status(self.playlist_result["status"])
        return self.playlist

    def parse_content_details(self) -> Playlist:
        if "contentDetails" in self.playlist_result:
            self.playlist.contentDetails = parse_content_details(
                self.playlist_result["contentDetails"]
            )
        return self.playlist

    def parse_player(self) -> Playlist:
        if "player" in self.playlist_result:
            self.playlist.player = parse_player(self.playlist_result["player"])
        return self.playlist


def parse_playlist(playlist_result: dict) -> Playlist:
    playlist = Playlist()
    playlist_parser = PlaylistParser(playlist_result, playlist)
    playlist_parser.parse_kind()
    playlist_parser.parse_id()
    playlist_parser.parse_etag()
    playlist_parser.parse_snippet()
    playlist_parser.parse_status()
    playlist_parser.parse_player()
    playlist_parser.parse_content_details()
    return playlist


def parse_playlist_list(playlist_result: list[dict]) -> list[Playlist]:
    playlists: list[Playlist] = list(map(parse_playlist, playlist_result))
    return playlists
