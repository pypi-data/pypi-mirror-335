from pydantic import BaseModel


class Localized(BaseModel):
    title: str
    description: str
