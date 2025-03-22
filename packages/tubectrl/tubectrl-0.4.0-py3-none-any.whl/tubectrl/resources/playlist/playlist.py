from typing import Iterator

from .playlist_iterator import PlaylistIterator


class YouTubePlaylistResource:
    def __init__(self, youtube_client):
        self.youtube_client = youtube_client

    def get_channel_playlists_iterator(
        self, channel_id: str, max_results: int = 25
    ) -> Iterator:
        return PlaylistIterator(
            youtube_client=self.youtube_client,
            channel_id=channel_id,
            max_results=max_results,
        )
