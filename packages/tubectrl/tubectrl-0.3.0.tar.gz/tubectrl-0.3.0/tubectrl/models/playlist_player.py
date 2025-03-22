from typing import Optional

from pydantic import Field

from .player import Player


class PlaylistPlayer(Player):
    embedHtml: Optional[str] = Field(default=None)
