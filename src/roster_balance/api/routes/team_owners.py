"""Team ownership API routes."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from roster_balance.api.auth import get_principal
from roster_balance.api.dependencies import get_team_ownership_service
from roster_balance.api.schemas import TeamOwnerResponse
from roster_balance.application.services.team_ownership_service import (
    LastOwnerError,
    OwnershipAuthorizationError,
    OwnershipNotFoundError,
    TeamOwnershipService,
)
from roster_balance.domain.models.principal import Principal

router = APIRouter(prefix='/teams/{team_id}/team-members', tags=['team-members'])
Ownership = Annotated[TeamOwnershipService, Depends(get_team_ownership_service)]
PrincipalDependency = Annotated[Principal, Depends(get_principal)]


@router.get('')
def list_team_members(
    team_id: str,
    service: Ownership,
    principal: PrincipalDependency,
    role: Annotated[Literal['owner'] | None, Query()] = None,
) -> list[TeamOwnerResponse]:
    try:
        service.require_member(team_id, principal.user_id)
    except OwnershipAuthorizationError as error:
        raise HTTPException(status_code=404, detail='Team not found') from error
    members = (
        service.list_owners(team_id)
        if role == 'owner'
        else service.list_members(team_id)
    )
    return [TeamOwnerResponse.model_validate(member) for member in members]


@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def remove_team_member(
    team_id: str,
    user_id: str,
    service: Ownership,
    principal: Annotated[Principal, Depends(get_principal)],
) -> Response:
    try:
        service.remove_member(team_id, user_id, principal)
    except OwnershipAuthorizationError as error:
        raise HTTPException(
            status_code=403, detail='Only team owners can modify membership'
        ) from error
    except OwnershipNotFoundError as error:
        raise HTTPException(status_code=404, detail='Team member not found') from error
    except LastOwnerError as error:
        raise HTTPException(
            status_code=409, detail='A team must retain an owner'
        ) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
