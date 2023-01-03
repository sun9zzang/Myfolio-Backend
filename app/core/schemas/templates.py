from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.core.schemas.users import User


class Template(BaseModel):
    id: int
    type: str
    title: str
    author: User
    likes: int
    created_at: datetime
    content: str


class TemplateInCreate(BaseModel):
    type: str
    title: str
    content: str


class TemplateInUpdate(BaseModel):
    id: int
    title: Optional[str] = None
    content: Optional[str] = None


class TemplateInList(BaseModel):
    id: int
    title: str
    author: User
    likes: int
    created_at: datetime


class TemplatesList(BaseModel):
    type: str
    templates: list[TemplateInList] = Field(default_factory=list)
    next_cursor: Optional[str] = None
