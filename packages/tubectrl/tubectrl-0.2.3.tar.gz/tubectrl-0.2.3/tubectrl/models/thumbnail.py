from typing import Optional

from pydantic import BaseModel


class Thumbnail(BaseModel):
    resolution: Optional[str] = None
    url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
