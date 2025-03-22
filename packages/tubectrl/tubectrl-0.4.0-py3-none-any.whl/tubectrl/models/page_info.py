from typing import Optional

from pydantic import BaseModel


class PageInfo(BaseModel):
    totalResults: Optional[int] = None
    resultsPerPage: Optional[int] = None
