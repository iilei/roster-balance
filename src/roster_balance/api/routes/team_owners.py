"""Team ownership API routes."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status

from roster_balance.api.auth import get_principal
from roster_balance.api.dependencies import get_team_ownership_service
from roster_balance.api.schemas import TeamOwnerResponse
from roster_balance.application.services.team_ownership_service import (
    LastOwnerError,
    OwnershipAuthorizationError,
    OwnershipConflictError,
    OwnershipNotFoundError,
    TeamOwnershipService,
)
from roster_balance.domain.models.principal import Principal

router = APIRouter(prefix="/teams/{team_id}/team-members", tags=["team-members"])
Ownership = Annotated[TeamOwnershipService, Depends(get_team_ownership_service)]


@router.get("")
def list_team_members(
    team_id: str,
    service: Ownership,
    role: Annotated[Literal["owner"] | None, Query()] = None,
) -> list[TeamOwnerResponse]:
    owners = service.list_owners(team_id) if role is None or role == "owner" else []
    return [TeamOwnerResponse.model_validate(owner) for owner in owners]


@router.put("/{user_id}", status_code=status.HTTP_201_CREATED)
def add_team_member(
    team_id: str,
    user_id: str,
    service: Ownership,
    principal: Annotated[Principal, Depends(get_principal)],
) -> TeamOwnerResponse:
    try:
        return TeamOwnerResponse.model_validate(
            service.add_owner(team_id, user_id, principal)
        )
    except OwnershipAuthorizationError as error:
        raise HTTPException(
            status_code=403, detail="Only team owners can modify ownership"
        ) from error
    except OwnershipConflictError as error:
        raise HTTPException(status_code=409, detail="User already owns team") from error


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_team_member(
    team_id: str,
    user_id: str,
    service: Ownership,
    principal: Annotated[Principal, Depends(get_principal)],
) -> None:
    try:
        service.remove_owner(team_id, user_id, principal)
    except OwnershipAuthorizationError as error:
        raise HTTPException(
            status_code=403, detail="Only team owners can modify ownership"
        ) from error
    except OwnershipNotFoundError as error:
        raise HTTPException(status_code=404, detail="Team owner not found") from error
    except LastOwnerError as error:
        raise HTTPException(
            status_code=409, detail="A team must retain an owner"
        ) from error
