"""Application services for secure team invitations."""

import contextlib
import hmac
import secrets
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from typing import Protocol
from uuid import uuid4

from roster_balance.application.services.team_ownership_service import (
    OwnershipAuthorizationError,
    OwnershipConflictError,
    TeamOwnershipService,
)
from roster_balance.application.services.user_service import UserService
from roster_balance.domain.models.principal import Principal
from roster_balance.domain.models.team_invitation import TeamInvitation
from roster_balance.domain.repositories.team_invitation_repository import (
    TeamInvitationRepository,
)


class InvitationSender(Protocol):
    def send(self, email: str, token: str) -> None: ...


class InvitationNotFoundError(LookupError):
    """Raised when an invitation does not exist."""


class InvitationTokenError(ValueError):
    """Raised when an invitation token is invalid."""


class InvitationExpiredError(ValueError):
    """Raised when an invitation has expired."""


class InvitationStateError(ValueError):
    """Raised when an invitation is no longer pending."""


class TeamInvitationService:
    def __init__(
        self,
        repository: TeamInvitationRepository,
        ownership_service: TeamOwnershipService,
        user_service: UserService,
        sender: InvitationSender,
        expiry: timedelta = timedelta(hours=4),
    ) -> None:
        self._repository = repository
        self._ownership_service = ownership_service
        self._user_service = user_service
        self._sender = sender
        self._expiry = expiry

    def create_invitation(
        self,
        team_id: str,
        email: str,
        principal: Principal,
    ) -> TeamInvitation:
        self._vacuum()
        if not self._ownership_service.is_owner(team_id, principal.user_id):
            raise OwnershipAuthorizationError(principal.user_id)
        normalized_email = self._normalize_email(email)
        now = datetime.now(UTC)
        token = secrets.token_urlsafe(32)
        invitation = TeamInvitation(
            id=str(uuid4()),
            team_id=team_id,
            inviter_user_id=principal.user_id,
            email=normalized_email,
            role='member',
            status='pending',
            token_hash=self._hash_token(token),
            created_at=now,
            expires_at=now + self._expiry,
        )
        saved = self._repository.add(invitation)
        self._sender.send(normalized_email, token)
        return saved

    def accept_invitation(
        self,
        invitation_id: str,
        token: str,
        principal: Principal,
    ) -> TeamInvitation:
        invitation = self._repository.get(invitation_id)
        if invitation is None:
            raise InvitationNotFoundError(invitation_id)
        if invitation.status != 'pending':
            raise InvitationStateError(invitation.status)
        now = datetime.now(UTC)
        if now >= invitation.expires_at:
            self._repository.purge_expired(now)
            raise InvitationExpiredError(invitation_id)
        if not hmac.compare_digest(invitation.token_hash, self._hash_token(token)):
            raise InvitationTokenError(invitation_id)
        user = self._user_service.resolve(principal)
        with contextlib.suppress(OwnershipConflictError):
            self._ownership_service.add_member_from_invitation(
                invitation.team_id,
                user.id,
            )
        accepted = replace(
            invitation,
            status='accepted',
            accepted_at=now,
            accepted_by_user_id=user.id,
        )
        return self._repository.save(accepted)

    def vacuum_expired(self) -> int:
        return self._vacuum()

    def _vacuum(self) -> int:
        return self._repository.purge_expired(datetime.now(UTC))

    def _normalize_email(self, email: str) -> str:
        normalized = email.strip().casefold()
        if not normalized or '@' not in normalized:
            raise ValueError('email must be valid')
        return normalized

    def _hash_token(self, token: str) -> str:
        return sha256(token.encode('utf-8')).hexdigest()
