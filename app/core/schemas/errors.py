from __future__ import annotations

from pydantic import BaseModel, Field, ValidationError


class Error(BaseModel):
    message: str
    code: str


class ErrorList(BaseModel):
    errors: list[Error] = Field(default_factory=list)

    def __init__(self, *args, **kwargs):
        param = []

        for arg in args:
            if type(arg) is Error:
                param.append(arg)
            elif type(arg) is list[Error]:
                param += arg
            else:
                raise ValidationError

        errors_kwarg = kwargs.get("errors")
        if type(errors_kwarg) is Error:
            param.append(errors_kwarg)
        elif type(errors_kwarg) is list[Error]:
            param += errors_kwarg
        else:
            raise ValidationError

        super().__init__(errors=param)

    def append(self, *errors: Error) -> ErrorList:
        self.errors += list(errors)
        return self
