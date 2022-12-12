from fastapi import APIRouter, Depends, Path, Query, status

from app.core.config import config
from app.core.errors.errors import ManagedErrors
from app.core.exceptions import HTTPException
from app.core.openapi import ResponseSchemaV1
from app.core.schemas.templates import TemplatesResponse
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
    current_user: UserInDB = Depends(get_current_user_authorizer()),
    templates_repo: TemplatesRepository = Depends(get_repository(TemplatesRepository)),
):
    raise NotImplementedError


@router.get(
    "/{template_id}",
    name=APINames.TEMPLATES_RETRIEVE_TEMPLATE_GET,
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
    name=APINames.TEMPLATES_RETRIEVE_TEMPLATES_LIST_GET,
    status_code=status.HTTP_200_OK,
    responses=ResponseSchemaV1.Templates.RETRIEVE_TEMPLATES_LIST,
)
async def retrieve_templates_list(
    page: int = Query(1, ge=1),
    limit: int = Query(
        config.TEMPLATES_LIST_DEFAULT_ITEM_LIMIT,
        ge=config.TEMPLATES_LIST_MIN_ITEM_LIMIT,
        le=config.TEMPLATES_LIST_MAX_ITEM_LIMIT,
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
    name=APINames.TEMPLATES_UPDATE_TEMPLATE_PATCH,
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
    name=APINames.TEMPLATES_DELETE_TEMPLATE_DELETE,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_template(
    template_id: int = Path(...),
    current_user: UserInDB = Depends(get_current_user_authorizer()),
    templates_repo: TemplatesRepository = Depends(get_repository(TemplatesRepository)),
):
    raise NotImplementedError
