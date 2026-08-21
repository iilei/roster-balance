"""SQLAlchemy-backed team invitation repository."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from sqlalchemy import select

from roster_balance.domain.models.team_invitation import TeamInvitation
from roster_balance.infrastructure.db.models import TeamInvitationModel

if TYPE_CHECKING:
    import builtins
    from datetime import datetime

    from sqlalchemy.orm import Session, sessionmaker

    from roster_balance.domain.models.team_invitation import (
        InvitationRole,
        InvitationStatus,
    )


class SQLAlchemyTeamInvitationRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def get(self, invitation_id: str) -> TeamInvitation | None:
        with self._session_factory.begin() as session:
            row = session.get(TeamInvitationModel, invitation_id)
            return None if row is None else self._to_domain(row)

    def find_pending(self, team_id: str, email: str) -> TeamInvitation | None:
        with self._session_factory.begin() as session:
            row = session.scalar(
                select(TeamInvitationModel).where(
                    TeamInvitationModel.team_id == team_id,
                    TeamInvitationModel.email == email,
                    TeamInvitationModel.status == 'pending',
                )
            )
            return None if row is None else self._to_domain(row)

    def list_for_team(self, team_id: str) -> builtins.list[TeamInvitation]:
        with self._session_factory.begin() as session:
            rows = session.scalars(
                select(TeamInvitationModel)
                .where(TeamInvitationModel.team_id == team_id)
                .order_by(TeamInvitationModel.created_at)
            ).all()
            return [self._to_domain(row) for row in rows]

    def add(self, invitation: TeamInvitation) -> TeamInvitation:
        with self._session_factory.begin() as session:
            row = TeamInvitationModel(
                id=invitation.id,
                team_id=invitation.team_id,
                inviter_user_id=invitation.inviter_user_id,
                email=invitation.email,
                role=invitation.role,
                status=invitation.status,
                token_hash=invitation.token_hash,
                created_at=invitation.created_at,
                expires_at=invitation.expires_at,
                accepted_at=invitation.accepted_at,
                accepted_by_user_id=invitation.accepted_by_user_id,
            )
            session.add(row)
            session.flush()
            return self._to_domain(row)

    def save(self, invitation: TeamInvitation) -> TeamInvitation:
        with self._session_factory.begin() as session:
            row = session.get(TeamInvitationModel, invitation.id)
            if row is None:
                raise LookupError(invitation.id)
            row.team_id = invitation.team_id
            row.inviter_user_id = invitation.inviter_user_id
            row.email = invitation.email
            row.role = invitation.role
            row.status = invitation.status
            row.token_hash = invitation.token_hash
            row.created_at = invitation.created_at
            row.expires_at = invitation.expires_at
            row.accepted_at = invitation.accepted_at
            row.accepted_by_user_id = invitation.accepted_by_user_id
            session.flush()
            return self._to_domain(row)

    def purge_expired(self, now: datetime) -> int:
        with self._session_factory.begin() as session:
            rows = session.scalars(
                select(TeamInvitationModel).where(
                    TeamInvitationModel.status == 'pending',
                    TeamInvitationModel.expires_at <= now,
                )
            ).all()
            for row in rows:
                session.delete(row)
            return len(rows)

    @staticmethod
    def _to_domain(row: TeamInvitationModel) -> TeamInvitation:
        return TeamInvitation(
            id=row.id,
            team_id=row.team_id,
            inviter_user_id=row.inviter_user_id,
            email=row.email,
            role=cast('InvitationRole', row.role),
            status=cast('InvitationStatus', row.status),
            token_hash=row.token_hash,
            created_at=row.created_at,
            expires_at=row.expires_at,
            accepted_at=row.accepted_at,
            accepted_by_user_id=row.accepted_by_user_id,
        )
