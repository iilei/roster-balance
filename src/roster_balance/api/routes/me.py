"""Current-user API routes."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query

from roster_balance.api.auth import get_principal
from roster_balance.api.dependencies import get_team_service, get_user_service
from roster_balance.api.schemas import (
    MeResponse,
    TeamMembershipResponse,
    TeamResponse,
    UserResponse,
)
from roster_balance.application.services.team_service import TeamService
from roster_balance.application.services.user_service import UserService
from roster_balance.domain.models.principal import Principal

router = APIRouter(tags=['identity'])


@router.get('/me')
def get_me(
    principal: Annotated[Principal, Depends(get_principal)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> MeResponse:
    user = service.resolve(principal)
    return MeResponse(
        principal=principal.user_id,
        user=UserResponse.model_validate(user),
    )


@router.get('/me/teams')
def list_my_teams(
    principal: Annotated[Principal, Depends(get_principal)],
    service: Annotated[TeamService, Depends(get_team_service)],
    role: Annotated[Literal['owner', 'member'] | None, Query()] = None,
) -> list[TeamMembershipResponse]:
    return [
        TeamMembershipResponse(
            team=TeamResponse.model_validate(team),
            role=membership.role,
        )
        for team, membership in service.list_teams_for_user(principal.user_id, role)
    ]
