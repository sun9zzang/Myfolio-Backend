from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.core.schemas.users import User


class TemplateBase(BaseModel):
    template_id: Optional[int] = None
    title: str
    likes: int = 0
    created_date: Optional[datetime] = None
    user: User


class UserInTemplateInList(BaseModel):
    user_id: int
    username: str


class TemplateInList(TemplateBase):
    template_id: int
    created_date: datetime
    user: UserInTemplateInList

    class Config:
        orm_mode = True


class TemplatesResponse(BaseModel):
    templates: list[TemplateInList] = Field(default_factory=list)


class Template(TemplateBase):
    template_id: int
    created_date: datetime
    content: str

    class Config:
        orm_mode = True
