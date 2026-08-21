"""Team invitation API routes."""

import os
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from roster_balance.api.auth import get_principal
from roster_balance.api.dependencies import (
    get_mailto_invitation_sender,
    get_team_invitation_service,
)
from roster_balance.api.schemas import (
    LocalInvitationDeliveryResponse,
    TeamInvitationAccept,
    TeamInvitationCreate,
    TeamInvitationPreviewResponse,
    TeamInvitationResponse,
    TeamInvitationSubmissionResponse,
)
from roster_balance.application.services.team_invitation_service import (
    InvitationExpiredError,
    InvitationNotFoundError,
    InvitationRecipientError,
    InvitationResendCooldownError,
    InvitationStateError,
    InvitationTokenError,
    TeamInvitationService,
)
from roster_balance.application.services.team_ownership_service import (
    OwnershipAuthorizationError,
)
from roster_balance.domain.models.principal import Principal
from roster_balance.infrastructure.email.mailto_invitation_sender import (
    MailtoInvitationSender,
)

router = APIRouter(tags=['invitations'])
Invitation = Annotated[TeamInvitationService, Depends(get_team_invitation_service)]
PrincipalDependency = Annotated[Principal, Depends(get_principal)]
MailtoSender = Annotated[MailtoInvitationSender, Depends(get_mailto_invitation_sender)]


@router.post(
    '/teams/{team_id}/invitations',
    status_code=status.HTTP_202_ACCEPTED,
)
def create_invitation(
    team_id: str,
    payload: TeamInvitationCreate,
    service: Invitation,
    principal: PrincipalDependency,
) -> TeamInvitationSubmissionResponse:
    try:
        service.create_invitation(team_id, payload.email, principal)
        return TeamInvitationSubmissionResponse(status='accepted_for_delivery')
    except OwnershipAuthorizationError as error:
        raise HTTPException(
            status_code=403,
            detail='Only team owners can invite members',
        ) from error
    except InvitationResendCooldownError:
        return TeamInvitationSubmissionResponse(status='accepted_for_delivery')


@router.get('/dev/invitations/latest/delivery')
def get_latest_local_delivery(
    sender: MailtoSender,
) -> LocalInvitationDeliveryResponse:
    if os.getenv('AUTHENTICATION_MODE', 'local') != 'local':
        raise HTTPException(status_code=404, detail='Not found')
    delivery = sender.latest()
    if delivery is None:
        raise HTTPException(status_code=404, detail='Delivery not found')
    return LocalInvitationDeliveryResponse.model_validate(delivery)


@router.get('/dev/invitations/{invitation_id}/delivery')
def get_local_delivery(
    invitation_id: str,
    sender: MailtoSender,
) -> LocalInvitationDeliveryResponse:
    if os.getenv('AUTHENTICATION_MODE', 'local') != 'local':
        raise HTTPException(status_code=404, detail='Not found')
    delivery = sender.get(invitation_id)
    if delivery is None:
        raise HTTPException(status_code=404, detail='Delivery not found')
    return LocalInvitationDeliveryResponse.model_validate(delivery)


@router.get('/invitations/{invitation_id}/preview')
def preview_invitation(
    invitation_id: str,
    token: Annotated[str, Query(min_length=1, max_length=512)],
    service: Invitation,
) -> TeamInvitationPreviewResponse:
    try:
        invitation = service.preview_invitation(invitation_id, token)
        return TeamInvitationPreviewResponse(
            team_id=invitation.team_id,
            role=invitation.role,
            expires_at=invitation.expires_at,
        )
    except InvitationNotFoundError as error:
        raise HTTPException(status_code=404, detail='Invitation not found') from error
    except InvitationTokenError as error:
        raise HTTPException(
            status_code=401, detail='Invalid invitation token'
        ) from error
    except InvitationExpiredError as error:
        raise HTTPException(status_code=410, detail='Invitation expired') from error
    except InvitationStateError as error:
        raise HTTPException(
            status_code=409, detail='Invitation is no longer pending'
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
    except InvitationRecipientError as error:
        raise HTTPException(
            status_code=403, detail='Invitation recipient mismatch'
        ) from error
    except InvitationStateError as error:
        raise HTTPException(
            status_code=409,
            detail='Invitation is no longer pending',
        ) from error
