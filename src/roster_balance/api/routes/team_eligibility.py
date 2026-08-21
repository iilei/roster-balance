"""Roster eligibility API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from roster_balance.api.auth import get_principal
from roster_balance.api.dependencies import get_team_eligibility_service
from roster_balance.api.schemas import TeamEligibilityResponse
from roster_balance.application.services.team_eligibility_service import (
    EligibilityConflictError,
    EligibilityNotFoundError,
    TeamEligibilityService,
)
from roster_balance.application.services.team_ownership_service import (
    OwnershipAuthorizationError,
)
from roster_balance.domain.models.principal import Principal

router = APIRouter(
    prefix="/teams/{team_id}/eligible-members", tags=["eligible-members"]
)
Eligibility = Annotated[TeamEligibilityService, Depends(get_team_eligibility_service)]
PrincipalDependency = Annotated[Principal, Depends(get_principal)]


@router.get("")
def list_eligible(team_id: str, service: Eligibility) -> list[TeamEligibilityResponse]:
    return [
        TeamEligibilityResponse.model_validate(member)
        for member in service.list_eligible(team_id)
    ]


@router.put("/{member_id}", status_code=status.HTTP_201_CREATED)
def add_eligible(
    team_id: str,
    member_id: str,
    service: Eligibility,
    principal: PrincipalDependency,
) -> TeamEligibilityResponse:
    try:
        return TeamEligibilityResponse.model_validate(
            service.add_eligible(team_id, member_id, principal)
        )
    except OwnershipAuthorizationError as error:
        raise HTTPException(
            status_code=403, detail="Only team owners can modify eligibility"
        ) from error
    except EligibilityConflictError as error:
        raise HTTPException(
            status_code=409, detail="Member is already eligible"
        ) from error


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_eligible(
    team_id: str,
    member_id: str,
    service: Eligibility,
    principal: PrincipalDependency,
) -> None:
    try:
        service.remove_eligible(team_id, member_id, principal)
    except OwnershipAuthorizationError as error:
        raise HTTPException(
            status_code=403, detail="Only team owners can modify eligibility"
        ) from error
    except EligibilityNotFoundError as error:
        raise HTTPException(
            status_code=404, detail="Eligible member not found"
        ) from error
