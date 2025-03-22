from pydantic import BaseModel, Field


class RegionRestriction(BaseModel):
    allowed: list[str] = Field(default_factory=list)
    blocked: list[str] = Field(default_factory=list)
