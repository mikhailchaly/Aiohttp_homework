from typing import Optional
import json

from pydantic import BaseModel, validator
from aiohttp import web


class CreateAdvert(BaseModel):
    title: str
    description: str
    owner: str

    @validator("title")
    def len_title(cls, value):
        if len(value) < 3:
            raise web.HTTPConflict(
                text=json.dumps({"error": "title is to short"}),
                content_type="application/json",
            )
        return value


class UpdateAdvert(BaseModel):
    title: Optional[str]
    description: Optional[str]
    owner: Optional[str]

    @validator("title")
    def len_title(cls, value):
        if len(value) < 3:
            raise web.HTTPConflict(
                text=json.dumps({"error": "title is to short"}),
                content_type="application/json",
            )
        return value
