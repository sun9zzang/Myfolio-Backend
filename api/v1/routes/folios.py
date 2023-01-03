import base64

from fastapi import APIRouter, Body, Depends, Path, Query, Response, status

from app.core.exceptions import HTTPException
from app.core.schemas.users import User, UserInDB
from app.core.strings import APINames
from app.db.repositories.templates import TemplatesRepository
from app.db.repositories.folios import FoliosRepository
from app.dependencies.repositories import get_repository
from app.core.schemas.folios import (
    FolioInCreate,
    FolioInUpdate,
)
from app.db.errors import EntityDoesNotExist
from app.core.errors.errors import ManagedErrors
from app.dependencies.auth import get_current_user_authorizer

router = APIRouter()


@router.post(
    "",
    name=APINames.FOLIOS_CREATE_FOLIO_POST,
    status_code=status.HTTP_201_CREATED,
    # responses=,
)
async def create_folio(
    folio_in_create: FolioInCreate = Body(...),
    current_user: UserInDB = Depends(get_current_user_authorizer()),
    templates_repo: TemplatesRepository = Depends(
        get_repository(TemplatesRepository)
    ),
    folios_repo: FoliosRepository = Depends(get_repository(FoliosRepository)),
):
    try:
        # todo optimize - check if target template exists or not
        templates_repo.retrieve_template_by_id(
            folio_in_create.base_template_id
        )
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            errors=ManagedErrors.not_found,
        )

    folio = folios_repo.create_folio(current_user.id, folio_in_create)

    return folio


@router.get(
    "",
    name=APINames.FOLIOS_RETRIEVE_FOLIOS_LIST_GET,
    status_code=status.HTTP_200_OK,
)
async def retrieve_folios_list(
    cursor: str = Query(""),
    limit: int = Query(10),
    current_user: UserInDB = Depends(get_current_user_authorizer()),
    folios_repo: FoliosRepository = Depends(get_repository(FoliosRepository)),
):
    cursor_decoded = base64.b64decode(cursor).decode("utf-8") if cursor else ""

    folios_list = folios_repo.retrieve_folios_list(
        current_user.id, cursor_decoded, limit
    )

    return folios_list


@router.get(
    "/{folio_id}",
    name=APINames.FOLIOS_RETRIEVE_FOLIO_GET,
    status_code=status.HTTP_200_OK,
)
async def retrieve_folio(
    folio_id: int = Path(...),
    current_user: UserInDB = Depends(get_current_user_authorizer()),
    folios_repo: FoliosRepository = Depends(get_repository(FoliosRepository)),
):
    not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        errors=ManagedErrors.not_found,
    )

    try:
        author_id_from_folio = folios_repo.retrieve_author_id_by_folio_id(
            folio_id
        )
    except EntityDoesNotExist:
        raise not_found

    if author_id_from_folio != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            errors=ManagedErrors.forbidden,
        )

    # todo exception handling needed?
    try:
        folio = folios_repo.retrieve_folio_by_id(folio_id)
    except EntityDoesNotExist:
        raise not_found

    return folio


@router.patch(
    "",
    name=APINames.FOLIOS_UPDATE_FOLIO_PATCH,
    status_code=status.HTTP_200_OK,
)
async def update_folio(
    folio_in_update: FolioInUpdate = Body(...),
    current_user: UserInDB = Depends(get_current_user_authorizer()),
    folios_repo: FoliosRepository = Depends(get_repository(FoliosRepository)),
):
    not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        errors=ManagedErrors.not_found,
    )

    try:
        author_id_from_folio = folios_repo.retrieve_author_id_by_folio_id(
            folio_in_update.id
        )
    except EntityDoesNotExist:
        raise not_found

    if author_id_from_folio != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            errors=ManagedErrors.forbidden,
        )

    try:
        folio = folios_repo.update_folio(folio_in_update)
    except EntityDoesNotExist:
        raise not_found

    return folio


@router.delete(
    "/{folio_id}",
    name=APINames.FOLIOS_DELETE_FOLIO_DELETE,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_folio(
    folio_id: int = Path(...),
    current_user: UserInDB = Depends(get_current_user_authorizer()),
    folios_repo: FoliosRepository = Depends(get_repository(FoliosRepository)),
):
    not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        errors=ManagedErrors.not_found,
    )

    try:
        user_id_from_folio = folios_repo.retrieve_author_id_by_folio_id(
            folio_id
        )
    except EntityDoesNotExist:
        raise not_found

    if user_id_from_folio != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            errors=ManagedErrors.forbidden,
        )

    try:
        folios_repo.delete_folio(folio_id)
    except EntityDoesNotExist:
        raise not_found

    return Response(status_code=status.HTTP_204_NO_CONTENT)
