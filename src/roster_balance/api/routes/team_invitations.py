"""Team invitation API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from roster_balance.api.auth import get_principal
from roster_balance.api.dependencies import get_team_invitation_service
from roster_balance.api.schemas import (
    TeamInvitationAccept,
    TeamInvitationCreate,
    TeamInvitationResponse,
)
from roster_balance.application.services.team_invitation_service import (
    InvitationExpiredError,
    InvitationNotFoundError,
    InvitationStateError,
    InvitationTokenError,
    TeamInvitationService,
)
from roster_balance.application.services.team_ownership_service import (
    OwnershipAuthorizationError,
)
from roster_balance.domain.models.principal import Principal

router = APIRouter(tags=['invitations'])
Invitation = Annotated[TeamInvitationService, Depends(get_team_invitation_service)]
PrincipalDependency = Annotated[Principal, Depends(get_principal)]


@router.post(
    '/teams/{team_id}/invitations',
    status_code=status.HTTP_202_ACCEPTED,
)
def create_invitation(
    team_id: str,
    payload: TeamInvitationCreate,
    service: Invitation,
    principal: PrincipalDependency,
) -> TeamInvitationResponse:
    try:
        return TeamInvitationResponse.model_validate(
            service.create_invitation(team_id, payload.email, principal),
        )
    except OwnershipAuthorizationError as error:
        raise HTTPException(
            status_code=403,
            detail='Only team owners can invite members',
        ) from error


@router.post(
    '/invitations/{invitation_id}/accept',
)
def accept_invitation(
    invitation_id: str,
    payload: TeamInvitationAccept,
    service: Invitation,
    principal: PrincipalDependency,
) -> TeamInvitationResponse:
    try:
        return TeamInvitationResponse.model_validate(
            service.accept_invitation(invitation_id, payload.token, principal),
        )
    except InvitationNotFoundError as error:
        raise HTTPException(status_code=404, detail='Invitation not found') from error
    except InvitationTokenError as error:
        raise HTTPException(
            status_code=401,
            detail='Invalid invitation token',
        ) from error
    except InvitationExpiredError as error:
        raise HTTPException(status_code=410, detail='Invitation expired') from error
    except InvitationStateError as error:
        raise HTTPException(
            status_code=409,
            detail='Invitation is no longer pending',
        ) from error
