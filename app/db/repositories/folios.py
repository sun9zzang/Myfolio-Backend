import base64

from sqlalchemy import select, and_, text
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import func

from app.core.models.users import TblUsers
from app.core.schemas.folios import (
    FolioInCreate,
    FolioInUpdate,
    Folio,
    TemplateInFolio,
    FolioInList,
    FoliosList,
)
from app.core.models.templates import TblTemplates
from app.core.models.folios import TblFolios
from app.core.schemas.users import User
from app.db.repositories.base import BaseRepository
from app.db.errors import EntityDoesNotExist


class FoliosRepository(BaseRepository):
    @staticmethod
    def _convert_folio_from_model_to_schema(
        folio_model: TblFolios,
        session: Session,
    ) -> Folio:
        author = session.get(TblUsers, folio_model.author_id)

        # todo add entity context to the exception
        if author is None:
            raise EntityDoesNotExist

        return Folio(
            id=folio_model.id,
            type=folio_model.type,
            title=folio_model.title,
            author=User.from_orm(author),
            base_template=TemplateInFolio(
                id=folio_model.base_template_id,
                content=folio_model.base_template_content,
                fetched_at=folio_model.base_template_fetched_at,
            ),
            user_input_data=folio_model.user_input_data,
            last_modified=folio_model.last_modified,
        )

    def create_folio(
        self, author_id: int, folio_in_create: FolioInCreate
    ) -> Folio:
        with self.get_session() as session:
            base_template = session.get(
                TblTemplates, folio_in_create.base_template_id
            )

            if base_template is None:
                raise EntityDoesNotExist

            base_template: TblTemplates

            folio_model = TblFolios(
                type=folio_in_create.type,
                title=folio_in_create.title,
                author_id=author_id,
                base_template_id=folio_in_create.base_template_id,
                base_template_content=base_template.content,
            )

            session.add(folio_model)
            session.commit()

            folio_schema = self._convert_folio_from_model_to_schema(
                folio_model, session
            )
            return folio_schema

    def retrieve_folio_by_id(self, folio_id: int) -> Folio:
        with self.get_session() as session:
            folio_model = session.get(TblFolios, folio_id)

            folio_schema = self._convert_folio_from_model_to_schema(
                folio_model, session
            )
            return folio_schema

    def retrieve_author_id_by_folio_id(self, folio_id: int) -> int:
        with self.get_session() as session:
            folio = session.get(TblFolios, folio_id)

            if folio is None:
                raise EntityDoesNotExist

            folio: TblFolios
            return folio.author_id

    def retrieve_folios_list(
        self, author_id: int, last_cursor: str, limit: int
    ) -> FoliosList:
        with self.get_session() as session:
            author = session.get(TblUsers, author_id)

            if author is None:
                raise EntityDoesNotExist

            cursor = func.concat(
                func.lpad(
                    func.date_format(
                        TblFolios.last_modified, "%Y%m%d%H%i%s%f"
                    ),
                    20,
                    "0",
                ),
                func.lpad(TblFolios.id, 10, "0"),
            ).label("cursor")

            query = (
                select(
                    cursor,
                    TblFolios.id,
                    TblFolios.type,
                    TblFolios.title,
                    TblFolios.last_modified,
                )
                .filter(TblFolios.author_id == author_id)
                .order_by(cursor.desc())
                .limit(limit)
            )
            if last_cursor:
                query = query.filter(cursor < text(last_cursor))

            result = session.execute(query).all()

            folios_list = [
                FolioInList(
                    id=row[1],
                    type=row[2],
                    title=row[3],
                    last_modified=row[4],
                )
                for row in result
            ]

            next_cursor = None
            if len(result):
                next_cursor = base64.b64encode(
                    result[len(result) - 1][0].encode("utf-8")
                )

            return FoliosList(
                author=User.from_orm(author),
                folios=folios_list,
                next_cursor=next_cursor,
            )

    def update_folio(self, folio_in_update: FolioInUpdate) -> Folio:
        with self.get_session() as session:
            folio_model = session.get(TblFolios, folio_in_update.id)

            if folio_model is None:
                raise EntityDoesNotExist

            folio_model: TblFolios

            if folio_in_update.title:
                folio_model.title = folio_in_update.title
            if folio_in_update.user_input_data:
                folio_model.user_input_data = folio_in_update.user_input_data

            session.commit()

            folio_schema = self._convert_folio_from_model_to_schema(
                folio_model, session
            )
            return folio_schema

    def delete_folio(self, folio_id: int) -> None:
        with self.get_session() as session:
            folio = session.get(TblFolios, folio_id)

            if folio is None:
                raise EntityDoesNotExist

            session.delete(folio)
            session.commit()
