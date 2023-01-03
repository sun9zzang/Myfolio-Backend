from __future__ import annotations

from pydantic import BaseModel, Field, ValidationError


class Error(BaseModel):
    message: str
    code: str


class ErrorList(BaseModel):
    errors: list[Error] = Field(default_factory=list)

    def __init__(self, *args, **kwargs):
        param_list = []

        for arg in args:
            if type(arg) is Error:
                param_list.append(arg)
            elif type(arg) is list[Error]:
                param_list += arg
            else:
                raise ValueError

        errors_kwarg = kwargs.get("errors", None)
        if errors_kwarg:
            if type(errors_kwarg) is Error:
                param_list.append(errors_kwarg)
            elif type(errors_kwarg) is list[Error]:
                param_list += errors_kwarg
            else:
                raise ValueError

        super().__init__(errors=param_list)

    def append(self, *errors: Error) -> ErrorList:
        self.errors += list(errors)
        return self
