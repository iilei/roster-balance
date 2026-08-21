"""SQLAlchemy persistence models.

These classes describe storage only; domain behavior belongs elsewhere.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TeamModel(Base):
    __tablename__ = 'teams'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String(2000))
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class UserModel(Base):
    __tablename__ = 'users'

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(320))
    display_name: Mapped[str | None] = mapped_column(String(200))
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    __table_args__ = (
        UniqueConstraint('provider', 'subject', name='uq_users_provider_subject'),
        Index('ix_users_email', 'email'),
    )


class TeamMembershipModel(Base):
    __tablename__ = 'team_memberships'

    team_id: Mapped[str] = mapped_column(
        String(36), ForeignKey('teams.id', ondelete='CASCADE'), primary_key=True
    )
    user_id: Mapped[str] = mapped_column(
        String(255), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True
    )
    role: Mapped[str] = mapped_column(String(32), nullable=False, default='member')
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class TeamDutyRoleModel(Base):
    __tablename__ = 'team_duty_roles'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    team_id: Mapped[str] = mapped_column(
        String(36), ForeignKey('teams.id', ondelete='CASCADE'), nullable=False
    )
    slug: Mapped[str] = mapped_column(String(80), nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(2000))
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    __table_args__ = (
        UniqueConstraint('team_id', 'slug', name='uq_team_duty_roles_team_slug'),
    )


class TeamEligibilityModel(Base):
    __tablename__ = 'team_roster_eligibility'

    team_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    member_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    duty_role_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey('team_duty_roles.id', ondelete='CASCADE'),
        primary_key=True,
    )
    duty_role: Mapped[str] = mapped_column(String(80), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ['team_id', 'member_id'],
            ['team_memberships.team_id', 'team_memberships.user_id'],
            ondelete='CASCADE',
        ),
    )


class TeamInvitationModel(Base):
    __tablename__ = 'team_invitations'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    team_id: Mapped[str] = mapped_column(
        String(36), ForeignKey('teams.id', ondelete='CASCADE'), nullable=False
    )
    inviter_user_id: Mapped[str] = mapped_column(
        String(255), ForeignKey('users.id', ondelete='RESTRICT'), nullable=False
    )
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False, default='member')
    status: Mapped[str] = mapped_column(String(32), nullable=False, default='pending')
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    accepted_by_user_id: Mapped[str | None] = mapped_column(
        String(255), ForeignKey('users.id', ondelete='SET NULL')
    )

    __table_args__ = (
        Index('ix_team_invitations_team_status', 'team_id', 'status'),
        Index('ix_team_invitations_email_status', 'email', 'status'),
        Index('ix_team_invitations_token_hash', 'token_hash'),
    )
