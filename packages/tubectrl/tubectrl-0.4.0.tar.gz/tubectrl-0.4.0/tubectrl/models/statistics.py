from typing import Optional

from pydantic import BaseModel, Field


class Statistics(BaseModel):
    viewCount: Optional[int] = Field(default=None)
    likeCount: Optional[int] = Field(default=None)
    dislikeCount: Optional[int] = Field(default=None)
    favoriteCount: Optional[int] = Field(default=None)
    commentCount: Optional[int] = Field(default=None)
