from sqlalchemy import select

from app.core.schemas.templates import TemplateInList
from app.core.models.templates import TblTemplates
from app.core.models.users import TblUsers
from app.db.repositories.base import BaseRepository


class TemplatesRepository(BaseRepository):
    def create_template(self):
        raise NotImplementedError

    def retrieve_template_by_id(self, template_id: int):
        raise NotImplementedError

    def retrieve_templates(self, offset: int, limit: int) -> list[TemplateInList]:
        query = (
            select(TblTemplates, TblUsers.username)
            .outerjoin(TblUsers)
            .order_by(TblTemplates.template_id.desc())
            .limit(limit)
            .offset((offset - 1) * limit)
        )
        with self.get_session() as session:
            # todo ordered by popularity, most viewed, etc.
            result = session.execute(query)
            return [
                TemplateInList(**row[0].__dict__, username=row[1]) for row in result
            ]

    def update_template(self):
        raise NotImplementedError

    def delete_template(self):
        raise NotImplementedError
