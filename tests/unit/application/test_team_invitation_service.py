from datetime import UTC, datetime, timedelta

import pytest

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
    OwnershipConflictError,
    TeamOwnershipService,
)
from roster_balance.application.services.user_service import UserService
from roster_balance.domain.models.principal import Principal
from roster_balance.domain.models.team_ownership import TeamOwnership
from roster_balance.infrastructure.email.in_memory_invitation_sender import (
    InMemoryInvitationSender,
)
from roster_balance.infrastructure.repositories.in_memory_team_invitation_repository import (
    InMemoryTeamInvitationRepository,
)
from roster_balance.infrastructure.repositories.in_memory_team_ownership_repository import (
    InMemoryTeamOwnershipRepository,
)
from roster_balance.infrastructure.repositories.in_memory_user_repository import (
    InMemoryUserRepository,
)


def make_service(
    expiry: timedelta = timedelta(days=7),
) -> tuple[
    TeamInvitationService,
    InMemoryInvitationSender,
    InMemoryTeamOwnershipRepository,
]:
    ownership_repository = InMemoryTeamOwnershipRepository()
    ownership_repository.add(
        TeamOwnership('team', 'local:owner', 'owner', datetime.now(UTC)),
    )
    sender = InMemoryInvitationSender()
    service = TeamInvitationService(
        InMemoryTeamInvitationRepository(),
        TeamOwnershipService(ownership_repository),
        UserService(InMemoryUserRepository()),
        sender,
        expiry=expiry,
    )
    return service, sender, ownership_repository


def test_invitation_normalizes_email_and_stores_only_a_hash() -> None:
    service, sender, _ = make_service()

    invitation = service.create_invitation(
        'team',
        '  Alice@Example.COM ',
        Principal('local', 'owner'),
    )

    assert invitation.email == 'alice@example.com'
    assert sender.sent[0][0] == 'alice@example.com'
    assert invitation.token_hash != sender.sent[0][1]


def test_non_owner_cannot_create_invitation() -> None:
    service, _, _ = make_service()

    with pytest.raises(OwnershipAuthorizationError):
        service.create_invitation(
            'team',
            'alice@example.com',
            Principal('local', 'other'),
        )


def test_acceptance_adds_member_and_cannot_be_replayed() -> None:
    service, sender, ownership_repository = make_service()
    invitation = service.create_invitation(
        'team',
        'alice@example.com',
        Principal('local', 'owner'),
    )

    accepted = service.accept_invitation(
        invitation.id,
        sender.sent[0][1],
        Principal('local', 'alice', 'alice@example.com'),
    )

    assert accepted.status == 'accepted'
    membership = ownership_repository.get('team', 'local:alice')
    assert membership is not None
    assert membership.role == 'member'
    with pytest.raises(InvitationStateError):
        service.accept_invitation(
            invitation.id,
            sender.sent[0][1],
            Principal('local', 'alice', 'alice@example.com'),
        )


def test_invalid_and_expired_tokens_are_rejected() -> None:
    service, sender, _ = make_service(expiry=timedelta(days=-1))
    invitation = service.create_invitation(
        'team',
        'alice@example.com',
        Principal('local', 'owner'),
    )

    with pytest.raises(InvitationExpiredError):
        service.accept_invitation(
            invitation.id,
            sender.sent[0][1],
            Principal('local', 'alice', 'alice@example.com'),
        )

    service, sender, _ = make_service()
    invitation = service.create_invitation(
        'team',
        'bob@example.com',
        Principal('local', 'owner'),
    )
    with pytest.raises(InvitationTokenError):
        service.accept_invitation(
            invitation.id,
            'wrong-token',
            Principal('local', 'bob', 'bob@example.com'),
        )


def test_vacuum_removes_expired_pending_invitations() -> None:
    service, _, _ = make_service(expiry=timedelta(days=-1))
    invitation = service.create_invitation(
        'team',
        'expired@example.com',
        Principal('local', 'owner'),
    )

    assert service.vacuum_expired() == 1
    with pytest.raises(InvitationNotFoundError):
        service.accept_invitation(
            invitation.id,
            'expired-token',
            Principal('local', 'expired', 'expired@example.com'),
        )


def test_wrong_recipient_cannot_accept_valid_token() -> None:
    service, sender, _ = make_service()
    invitation = service.create_invitation(
        'team', 'alice@example.com', Principal('local', 'owner')
    )

    with pytest.raises(InvitationRecipientError):
        service.accept_invitation(
            invitation.id,
            sender.sent[0][1],
            Principal('local', 'bob', 'bob@example.com'),
        )


def test_accepting_invitation_for_an_existing_member_is_rejected() -> None:
    service, sender, ownership_repository = make_service()
    ownership_repository.add(
        TeamOwnership('team', 'local:alice', 'member', datetime.now(UTC))
    )
    invitation = service.create_invitation(
        'team', 'alice@example.com', Principal('local', 'owner')
    )

    with pytest.raises(OwnershipConflictError):
        service.accept_invitation(
            invitation.id,
            sender.sent[0][1],
            Principal('local', 'alice', 'alice@example.com'),
        )


def test_preview_requires_the_valid_invitation_token() -> None:
    service, sender, _ = make_service()
    invitation = service.create_invitation(
        'team', 'alice@example.com', Principal('local', 'owner')
    )

    preview = service.preview_invitation(invitation.id, sender.sent[0][1])

    assert preview.team_id == 'team'
    assert preview.role == 'member'
    with pytest.raises(InvitationTokenError):
        service.preview_invitation(invitation.id, 'wrong-token')


def test_resend_is_blocked_during_cooldown() -> None:
    service, _, _ = make_service(expiry=timedelta(hours=4))
    principal = Principal('local', 'owner')
    service.create_invitation('team', 'alice@example.com', principal)

    with pytest.raises(InvitationResendCooldownError):
        service.create_invitation('team', 'ALICE@example.com', principal)
