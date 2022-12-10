from typing import Callable, Type

from app.db.repositories.base import BaseRepository


def get_repository(
    repo_type: Type[BaseRepository],
) -> Callable[[], BaseRepository]:
    def _get_repo() -> BaseRepository:
        return repo_type()

    return _get_repo
