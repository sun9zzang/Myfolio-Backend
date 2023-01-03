from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.core.schemas.users import User


class TemplateInFolio(BaseModel):
    id: int
    content: str
    fetched_at: datetime


class Folio(BaseModel):
    id: int
    type: str
    title: str
    author: User
    base_template: TemplateInFolio
    user_input_data: str
    last_modified: datetime


class FolioInCreate(BaseModel):
    type: str
    base_template_id: int
    title: str


class FolioInUpdate(BaseModel):
    id: int
    title: str
    user_input_data: str


class FolioInList(BaseModel):
    id: int
    type: str
    title: str
    last_modified: datetime


class FoliosList(BaseModel):
    author: User
    folios: list[FolioInList] = Field(default_factory=list)
    next_cursor: Optional[str]
