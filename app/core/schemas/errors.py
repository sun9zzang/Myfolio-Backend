from __future__ import annotations

from pydantic import BaseModel


class Error(BaseModel):
    message: str
    code: str


class ErrorList(BaseModel):
    errors: list[Error] = []

    def append(self, *errors: Error) -> ErrorList:
        self.errors += list(errors)
        return self
