"""Team duty-role configuration API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from roster_balance.api.auth import get_principal
from roster_balance.api.dependencies import (
    get_team_duty_role_service,
    get_team_ownership_service,
)
from roster_balance.api.schemas import TeamDutyRoleCreate, TeamDutyRoleResponse
from roster_balance.application.services.team_duty_role_service import (
    DutyRoleConflictError,
    DutyRoleNotFoundError,
    TeamDutyRoleService,
)
from roster_balance.application.services.team_ownership_service import (
    OwnershipAuthorizationError,
    TeamOwnershipService,
)
from roster_balance.domain.models.principal import Principal

router = APIRouter(prefix='/teams/{team_id}/duty-roles', tags=['duty-roles'])
DutyRoles = Annotated[TeamDutyRoleService, Depends(get_team_duty_role_service)]
Ownership = Annotated[TeamOwnershipService, Depends(get_team_ownership_service)]
PrincipalDependency = Annotated[Principal, Depends(get_principal)]


@router.get('')
def list_roles(
    team_id: str,
    service: DutyRoles,
    ownership: Ownership,
    principal: PrincipalDependency,
) -> list[TeamDutyRoleResponse]:
    try:
        ownership.require_member(team_id, principal.user_id)
    except OwnershipAuthorizationError as error:
        raise HTTPException(status_code=404, detail='Team not found') from error
    return [
        TeamDutyRoleResponse.model_validate(role)
        for role in service.list_roles(team_id)
    ]


@router.post('', status_code=status.HTTP_201_CREATED)
def create_role(
    team_id: str,
    payload: TeamDutyRoleCreate,
    service: DutyRoles,
    principal: PrincipalDependency,
) -> TeamDutyRoleResponse:
    try:
        return TeamDutyRoleResponse.model_validate(
            service.create_role(
                team_id,
                payload.slug,
                payload.display_name,
                payload.description,
                principal,
            )
        )
    except OwnershipAuthorizationError as error:
        raise HTTPException(
            status_code=403, detail='Only team owners can configure roles'
        ) from error
    except DutyRoleConflictError as error:
        raise HTTPException(
            status_code=409, detail='Duty role already exists'
        ) from error


@router.delete('/{role_id}', status_code=status.HTTP_204_NO_CONTENT)
def deactivate_role(
    team_id: str,
    role_id: str,
    service: DutyRoles,
    principal: PrincipalDependency,
) -> None:
    try:
        service.deactivate_role(team_id, role_id, principal)
    except OwnershipAuthorizationError as error:
        raise HTTPException(
            status_code=403, detail='Only team owners can configure roles'
        ) from error
    except DutyRoleNotFoundError as error:
        raise HTTPException(status_code=404, detail='Duty role not found') from error
