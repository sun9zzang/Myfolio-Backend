from fastapi import APIRouter, Depends, Path, Query, status

from app.core.config import settings
from app.core.errors.errors import ManagedErrors
from app.core.exceptions import HTTPException
from app.core.openapi import ResponseSchemaV1
from app.core.schemas.templates import TemplatesResponse
from app.core.schemas.users import UserInDB
from app.db.errors import EntityDoesNotExist
from app.db.repositories.templates import TemplatesRepository
from app.dependencies.auth import get_current_user_authorizer
from app.dependencies.repositories import get_repository

router = APIRouter()


@router.post(
    "",
    name="templates:create-template",
    status_code=status.HTTP_201_CREATED,
)
async def create_template(
    current_user: UserInDB = Depends(get_current_user_authorizer()),
    templates_repo: TemplatesRepository = Depends(get_repository(TemplatesRepository)),
):
    raise NotImplementedError


@router.get(
    "/{template_id}",
    name="templates:retrieve-template",
    status_code=status.HTTP_200_OK,
    responses=ResponseSchemaV1.Templates.RETRIEVE_TEMPLATE,
)
async def retrieve_template(
    template_id: int = Path(...),
    templates_repo: TemplatesRepository = Depends(get_repository(TemplatesRepository)),
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
    name="templates:retrieve-templates-list",
    status_code=status.HTTP_200_OK,
    responses=ResponseSchemaV1.Templates.RETRIEVE_TEMPLATES_LIST,
)
async def retrieve_templates_list(
    page: int = Query(1, ge=1),
    limit: int = Query(
        settings.DEFAULT_TEMPLATES_LIST_LIMIT,
        ge=settings.TEMPLATES_MIN_LIST_LIMIT,
        le=settings.TEMPLATES_MAX_LIST_LIMIT,
    ),
    templates_repo: TemplatesRepository = Depends(get_repository(TemplatesRepository)),
):
    templates_list = templates_repo.retrieve_templates(
        offset=page,
        limit=limit,
    )

    if not templates_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            errors=ManagedErrors.not_found,
        )

    return TemplatesResponse(templates=templates_list)


@router.patch(
    "",
    name="templates:update-template",
    status_code=status.HTTP_200_OK,
)
async def update_template(
    template_id: int = Path(...),
    current_user: UserInDB = Depends(get_current_user_authorizer()),
    templates_repo: TemplatesRepository = Depends(get_repository(TemplatesRepository)),
):
    raise NotImplementedError


@router.delete(
    "/{template_id}",
    name="template:delete-template",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_template(
    template_id: int = Path(...),
    current_user: UserInDB = Depends(get_current_user_authorizer()),
    templates_repo: TemplatesRepository = Depends(get_repository(TemplatesRepository)),
):
    raise NotImplementedError
