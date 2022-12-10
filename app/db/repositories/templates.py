from sqlalchemy import select

from app.core.models.templates import TblTemplates
from app.core.models.users import TblUsers
from app.core.schemas.templates import Template, TemplateInList
from app.db.errors import EntityDoesNotExist
from app.db.repositories.base import BaseRepository


class TemplatesRepository(BaseRepository):
    def create_template(self):
        raise NotImplementedError

    def retrieve_template_by_id(self, template_id: int):
        with self.get_session() as session:
            template = session.get(TblTemplates, template_id)
            if template is None:
                raise EntityDoesNotExist
            user = session.get(TblUsers, template.user_id)
            if user is None:
                raise EntityDoesNotExist  # todo error hanlding

            return Template(
                **template.__dict__,  # todo optimize
                user=user.__dict__,
            )

    def retrieve_templates(self, offset: int, limit: int) -> list[TemplateInList]:
        query = (
            select(
                TblTemplates.template_id,
                TblTemplates.title,
                TblTemplates.likes,
                TblTemplates.created_date,
                TblUsers.user_id,
                TblUsers.username,
            )
            .outerjoin(TblUsers)
            .order_by(TblTemplates.template_id.desc())
            .limit(limit)
            .offset((offset - 1) * limit)
        )
        with self.get_session() as session:
            # todo ordered by popularity, most viewed, etc.
            result = session.execute(query)
            return [
                TemplateInList(
                    template_id=row[0],
                    title=row[1],
                    likes=row[2],
                    created_date=row[3],
                    user={
                        "user_id": row[4],
                        "username": row[5],
                    },
                )
                for row in result
            ]

    def update_template(self):
        raise NotImplementedError

    def delete_template(self):
        raise NotImplementedError
