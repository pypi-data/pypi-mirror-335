from typing import Iterator

from .playlist_items_iterator import PlaylistItemIterator


class YouTubePlaylistItemResource:
    def __init__(self, youtube_client):
        self.youtube_client = youtube_client

    def get_playlist_items_iterator(
        self, playlist_id: str, max_results: int = 25
    ) -> Iterator:
        return PlaylistItemIterator(
            youtube_client=self.youtube_client,
            playlist_id=playlist_id,
            max_results=max_results,
        )
