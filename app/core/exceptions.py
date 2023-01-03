# Custom Exceptions
from typing import Optional, Union

from app.core.schemas.errors import Error


class HTTPException(Exception):
    def __init__(
        self,
        status_code: int,
        errors: Union[Error, list[Error]],
        headers: Optional[dict] = None,
    ) -> None:
        if type(errors) is Error:
            self.errors = [errors]
        elif type(errors) is list:
            for error in errors:
                if type(error) is not Error:
                    raise ValueError
            self.errors = errors
        else:
            raise ValueError
        self.status_code = status_code
        self.headers = headers

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(status_code={self.status_code!r}, errors={self.errors!r})"
