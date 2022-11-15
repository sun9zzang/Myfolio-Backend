from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TemplateBase(BaseModel):
    template_id: Optional[int] = None
    title: str
    likes: int = 0
    created_date: Optional[datetime] = None
    user_id: int


class TemplateInList(TemplateBase):
    template_id: int
    created_date: datetime
    username: str

    class Config:
        orm_mode = True


class TemplatesResponse(BaseModel):
    templates: list[TemplateInList] = Field(default_factory=list)


class Template(TemplateBase):
    template_id: int
    created_date: datetime
    content: bytes

    class Config:
        orm_mode = True
