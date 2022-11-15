# Custom Exceptions
from typing import Optional, Union

from app.core.schemas.errors import Error, ErrorList


class HTTPException(Exception):
    def __init__(
        self,
        status_code: int,
        errors: Union[Error, ErrorList],
        headers: Optional[dict] = None,
    ) -> None:
        self.status_code = status_code
        self.errors = errors
        self.headers = headers

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(status_code={self.status_code!r}, errors={self.errors!r})"
