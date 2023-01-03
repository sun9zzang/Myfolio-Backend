import base64

from fastapi import APIRouter, Body, Depends, Response, Path, Query, status

from app.core.config import config
from app.core.errors.errors import ManagedErrors
from app.core.exceptions import HTTPException
from app.core.openapi import ResponseSchemaV1
from app.core.schemas.templates import (
    TemplateInCreate,
    TemplateInUpdate,
)
from app.core.schemas.users import UserInDB
from app.db.errors import EntityDoesNotExist
from app.db.repositories.templates import TemplatesRepository
from app.dependencies.auth import get_current_user_authorizer
from app.dependencies.repositories import get_repository
from app.core.strings import APINames

router = APIRouter()


@router.post(
    "",
    name=APINames.TEMPLATES_CREATE_TEMPLATE_POST,
    status_code=status.HTTP_201_CREATED,
)
async def create_template(
    template_in_create: TemplateInCreate = Body(...),
    current_user: UserInDB = Depends(get_current_user_authorizer()),
    templates_repo: TemplatesRepository = Depends(
        get_repository(TemplatesRepository)
    ),
):
    if template_in_create.type not in ("portfolio", "resume"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=ManagedErrors.bad_request,
        )

    # todo validate fields

    template = templates_repo.create_template(
        current_user.id, template_in_create
    )

    return template


@router.get(
    "/{template_id}",
    name=APINames.TEMPLATES_RETRIEVE_TEMPLATE_GET,
    status_code=status.HTTP_200_OK,
    responses=ResponseSchemaV1.Templates.RETRIEVE_TEMPLATE,
)
async def retrieve_template(
    template_id: int = Path(...),
    templates_repo: TemplatesRepository = Depends(
        get_repository(TemplatesRepository)
    ),
):
    try:
        template = templates_repo.retrieve_template_by_id(template_id)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            errors=ManagedErrors.not_found,
        )

    return template


@router.get(
    "",
    name=APINames.TEMPLATES_RETRIEVE_TEMPLATES_LIST_GET,
    status_code=status.HTTP_200_OK,
    responses=ResponseSchemaV1.Templates.RETRIEVE_TEMPLATES_LIST,
)
async def retrieve_templates_list(
    templates_type: str = Query(..., alias="type"),
    cursor: str = Query(""),
    limit: int = Query(10),
    templates_repo: TemplatesRepository = Depends(
        get_repository(TemplatesRepository)
    ),
):
    # todo cursor validation
    cursor_decoded = base64.b64decode(cursor).decode("utf-8") if cursor else ""

    templates_list = templates_repo.retrieve_templates_list(
        templates_type, cursor_decoded, limit
    )

    # if not templates_list.templates:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         errors=ManagedErrors.not_found,
    #     )

    return templates_list


@router.patch(
    "",
    name=APINames.TEMPLATES_UPDATE_TEMPLATE_PATCH,
    status_code=status.HTTP_200_OK,
)
async def update_template(
    template_in_update: TemplateInUpdate = Body(...),
    current_user: UserInDB = Depends(get_current_user_authorizer()),
    templates_repo: TemplatesRepository = Depends(
        get_repository(TemplatesRepository)
    ),
):
    try:
        template_author_id = templates_repo.retrieve_author_id_by_template_id(
            template_in_update.id
        )
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            errors=ManagedErrors.not_found,
        )

    if template_author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            errors=ManagedErrors.forbidden,
        )

    if not (template_in_update.title or template_in_update.content):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=ManagedErrors.bad_request,
        )

    template = templates_repo.update_template(template_in_update)

    return template


@router.delete(
    "/{template_id}",
    name=APINames.TEMPLATES_DELETE_TEMPLATE_DELETE,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_template(
    template_id: int = Path(...),
    current_user: UserInDB = Depends(get_current_user_authorizer()),
    templates_repo: TemplatesRepository = Depends(
        get_repository(TemplatesRepository)
    ),
):
    not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        errors=ManagedErrors.not_found,
    )

    try:
        template_author_id = templates_repo.retrieve_author_id_by_template_id(
            template_id
        )
    except EntityDoesNotExist:
        raise not_found

    if template_author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            errors=ManagedErrors.forbidden,
        )

    try:
        templates_repo.delete_template(template_id)
    except EntityDoesNotExist:
        raise not_found

    return Response(status_code=status.HTTP_204_NO_CONTENT)
