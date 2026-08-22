"""Roster eligibility API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from roster_balance.api.auth import get_principal
from roster_balance.api.dependencies import (
    get_team_eligibility_service,
    get_team_ownership_service,
)
from roster_balance.api.schemas import TeamEligibilityCreate, TeamEligibilityResponse
from roster_balance.application.services.team_duty_role_service import (
    DutyRoleNotFoundError,
)
from roster_balance.application.services.team_eligibility_service import (
    DutyRoleInactiveError,
    EligibilityConflictError,
    EligibilityNotFoundError,
    TeamEligibilityService,
    TeamMemberNotFoundError,
)
from roster_balance.application.services.team_ownership_service import (
    OwnershipAuthorizationError,
    TeamOwnershipService,
)
from roster_balance.domain.models.principal import Principal

router = APIRouter(
    prefix='/teams/{team_id}/eligible-members',
    tags=['eligible-members'],
)
Eligibility = Annotated[TeamEligibilityService, Depends(get_team_eligibility_service)]
Ownership = Annotated[TeamOwnershipService, Depends(get_team_ownership_service)]
PrincipalDependency = Annotated[Principal, Depends(get_principal)]


@router.get('')
def list_eligible(
    team_id: str,
    service: Eligibility,
    ownership: Ownership,
    principal: PrincipalDependency,
) -> list[TeamEligibilityResponse]:
    try:
        ownership.require_member(team_id, principal.user_id)
    except OwnershipAuthorizationError as error:
        raise HTTPException(status_code=404, detail='Team not found') from error
    return [
        TeamEligibilityResponse.model_validate(member)
        for member in service.list_eligible(team_id)
    ]


@router.get('/{duty_role}')
def list_role_eligible(
    team_id: str,
    duty_role: str,
    service: Eligibility,
    ownership: Ownership,
    principal: PrincipalDependency,
) -> list[TeamEligibilityResponse]:
    try:
        ownership.require_member(team_id, principal.user_id)
        return [
            TeamEligibilityResponse.model_validate(member)
            for member in service.list_eligible(team_id, duty_role)
        ]
    except OwnershipAuthorizationError as error:
        raise HTTPException(status_code=404, detail='Team not found') from error
    except DutyRoleNotFoundError as error:
        raise HTTPException(status_code=404, detail='Duty role not found') from error


@router.post('/{duty_role}', status_code=status.HTTP_201_CREATED)
def add_eligible(
    team_id: str,
    duty_role: str,
    payload: TeamEligibilityCreate,
    service: Eligibility,
    principal: PrincipalDependency,
) -> TeamEligibilityResponse:
    try:
        return TeamEligibilityResponse.model_validate(
            service.add_eligible(team_id, payload.member_id, duty_role, principal),
        )
    except OwnershipAuthorizationError as error:
        raise HTTPException(
            status_code=403,
            detail='Only team owners can modify eligibility',
        ) from error
    except EligibilityConflictError as error:
        raise HTTPException(
            status_code=409,
            detail='Member is already eligible',
        ) from error
    except (DutyRoleNotFoundError, TeamMemberNotFoundError) as error:
        raise HTTPException(
            status_code=404, detail='Duty role or team member not found'
        ) from error
    except DutyRoleInactiveError as error:
        raise HTTPException(status_code=409, detail='Duty role is inactive') from error


@router.delete('/{duty_role}/{member_id}', status_code=status.HTTP_204_NO_CONTENT)
def remove_eligible(
    team_id: str,
    duty_role: str,
    member_id: str,
    service: Eligibility,
    principal: PrincipalDependency,
) -> None:
    try:
        service.remove_eligible(team_id, member_id, duty_role, principal)
    except OwnershipAuthorizationError as error:
        raise HTTPException(
            status_code=403,
            detail='Only team owners can modify eligibility',
        ) from error
    except EligibilityNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail='Eligible member not found',
        ) from error
