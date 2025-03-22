from typing import Optional

from pydantic import BaseModel, Field


class ResourceId(BaseModel):
    kind: Optional[str] = Field(default=None)
    videoId: Optional[str] = Field(default=None)
