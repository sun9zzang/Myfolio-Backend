import base64

from sqlalchemy import select, text
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import func

from app.core.models.templates import TblTemplates
from app.core.models.users import TblUsers
from app.core.schemas.templates import (
    Template,
    TemplateInList,
    TemplateInCreate,
    TemplatesList,
    TemplateInUpdate,
)
from app.core.schemas.users import User
from app.db.errors import EntityDoesNotExist
from app.db.repositories.base import BaseRepository


class TemplatesRepository(BaseRepository):
    @staticmethod
    def _convert_template_model_to_schema(
        template_model: TblTemplates, session: Session
    ) -> Template:
        author = session.get(TblUsers, template_model.author_id)

        # todo add entity context to the exception
        if author is None:
            raise EntityDoesNotExist

        return Template(
            id=template_model.id,
            type=template_model.type,
            title=template_model.title,
            author=User.from_orm(author),
            likes=template_model.likes,
            created_at=template_model.created_at,
            content=template_model.content,
        )

    def create_template(
        self, user_id: int, template_in_create: TemplateInCreate
    ) -> Template:
        template_model = TblTemplates(
            type=template_in_create.type,
            title=template_in_create.title,
            content=template_in_create.content,
            author_id=user_id,
        )

        with self.get_session() as session:
            session.add(template_model)
            session.commit()

            template_schema = self._convert_template_model_to_schema(
                template_model, session
            )
            return template_schema

    def retrieve_template_by_id(self, template_id: int) -> Template:
        with self.get_session() as session:
            template_model = session.get(TblTemplates, template_id)
            if template_model is None:
                raise EntityDoesNotExist

            template_schema = self._convert_template_model_to_schema(
                template_model, session
            )
            return template_schema

    def retrieve_author_id_by_template_id(self, template_id: int) -> int:
        with self.get_session() as session:
            template = session.get(TblTemplates, template_id)

            if template is None:
                raise EntityDoesNotExist

            template: TblTemplates

            return template.author_id

    def retrieve_templates_list(
        self, templates_type: str, last_cursor: str, limit: int
    ) -> TemplatesList:
        # todo ordered by popularity, most viewed, etc.
        cursor = func.concat(
            func.lpad(
                func.date_format(TblTemplates.created_at, "%Y%m%d%H%i%s%f"),
                20,
                "0",
            ),
            func.lpad(TblTemplates.id, 10, "0"),
        ).label("cursor")

        query = (
            select(
                cursor,
                TblTemplates.id,
                TblTemplates.title,
                TblTemplates.likes,
                TblTemplates.created_at,
                TblUsers.id,
                TblUsers.email,
                TblUsers.username,
            )
            .join(TblUsers, TblTemplates.author_id == TblUsers.id)
            .filter(TblTemplates.type == templates_type)
            .order_by(cursor.desc())
            .limit(limit)
        )
        if last_cursor:
            # query = query.filter("cursor" < last_cursor)
            query = query.filter(cursor < text(last_cursor))

        print(query)

        with self.get_session() as session:
            result = session.execute(query).all()

            print(result)

            templates_list = [
                TemplateInList(
                    id=row[1],
                    title=row[2],
                    author=User(
                        id=row[5],
                        email=row[6],
                        username=row[7],
                    ),
                    likes=row[3],
                    created_at=row[4],
                )
                for row in result
            ]

            next_cursor = None
            if len(result):
                next_cursor = base64.b64encode(
                    result[len(result) - 1][0].encode("utf-8")
                )

            print(next_cursor)

            return TemplatesList(
                type=templates_type,
                templates=templates_list,
                next_cursor=next_cursor,
            )

    def update_template(
        self, template_in_update: TemplateInUpdate
    ) -> Template:
        with self.get_session() as session:
            template_model = session.get(TblTemplates, template_in_update.id)

            if template_model is None:
                raise EntityDoesNotExist

            template_model: TblTemplates

            if template_in_update.title:
                template_model.title = template_in_update.title
            if template_in_update.content:
                template_model.content = template_in_update.content

            session.commit()

            template_schema = self._convert_template_model_to_schema(
                template_model, session
            )
            return template_schema

    def delete_template(self, template_id: int) -> None:
        with self.get_session() as session:
            template = session.get(TblTemplates, template_id)

            if template is None:
                raise EntityDoesNotExist

            session.delete(template)
            session.commit()
