from typing import Any

from ..models import Localized, Thumbnail


def parse_localized(localized_data: dict[str, Any]) -> Localized:
    pass


def parse_thumbnail(resolution: str, details: dict) -> Thumbnail:
    thumbnail: Thumbnail = Thumbnail()
    thumbnail.resolution = resolution
    if details.get("url"):
        thumbnail.url = details["url"]
    if details.get("width"):
        thumbnail.width = details["width"]
    if details.get("height"):
        thumbnail.height = details["height"]
    return thumbnail
