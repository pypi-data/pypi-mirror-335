from typing import Optional

from pydantic import BaseModel, Field

from .request_filter import Filter
from .request_optional_parameters import OptionalParameters
from .request_part import Part


class YouTubeRequest(BaseModel):
    part: Part
    filter: Optional[Filter] = Filter()
    optional_parameters: Optional[OptionalParameters] = OptionalParameters()
