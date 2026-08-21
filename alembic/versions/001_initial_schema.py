"""Create the initial operational schema.

Revision ID: 001_initial_schema
Revises:
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op  # type: ignore[attr-defined]

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = '001_initial_schema'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'teams',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.String(length=2000), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=255), nullable=False),
        sa.Column('provider', sa.String(length=64), nullable=False),
        sa.Column('subject', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=320), nullable=True),
        sa.Column('display_name', sa.String(length=200), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('provider', 'subject', name='uq_users_provider_subject'),
    )
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_table(
        'team_memberships',
        sa.Column('team_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column(
            'role', sa.String(length=32), nullable=False, server_default='member'
        ),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('team_id', 'user_id'),
        sa.CheckConstraint(
            "role IN ('owner', 'member')", name='ck_team_memberships_role'
        ),
    )
    op.create_table(
        'team_duty_roles',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('team_id', sa.String(length=36), nullable=False),
        sa.Column('slug', sa.String(length=80), nullable=False),
        sa.Column('display_name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.String(length=2000), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('team_id', 'slug', name='uq_team_duty_roles_team_slug'),
    )
    op.create_table(
        'team_roster_eligibility',
        sa.Column('team_id', sa.String(length=36), nullable=False),
        sa.Column('member_id', sa.String(length=255), nullable=False),
        sa.Column('duty_role_id', sa.String(length=36), nullable=False),
        sa.Column('duty_role', sa.String(length=80), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['team_id', 'member_id'],
            ['team_memberships.team_id', 'team_memberships.user_id'],
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['duty_role_id'], ['team_duty_roles.id'], ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('team_id', 'member_id', 'duty_role_id'),
    )
    op.create_table(
        'team_invitations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('team_id', sa.String(length=36), nullable=False),
        sa.Column('inviter_user_id', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=320), nullable=False),
        sa.Column(
            'role', sa.String(length=32), nullable=False, server_default='member'
        ),
        sa.Column(
            'status', sa.String(length=32), nullable=False, server_default='pending'
        ),
        sa.Column('token_hash', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('accepted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('accepted_by_user_id', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['inviter_user_id'], ['users.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(
            ['accepted_by_user_id'], ['users.id'], ondelete='SET NULL'
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("role IN ('member')", name='ck_team_invitations_role'),
        sa.CheckConstraint(
            "status IN ('pending', 'accepted', 'declined', 'expired')",
            name='ck_team_invitations_status',
        ),
    )
    op.create_index(
        'ix_team_invitations_team_status',
        'team_invitations',
        ['team_id', 'status'],
    )
    op.create_index(
        'ix_team_invitations_email_status',
        'team_invitations',
        ['email', 'status'],
    )
    op.create_index(
        'ix_team_invitations_token_hash', 'team_invitations', ['token_hash']
    )


def downgrade() -> None:
    op.drop_index('ix_team_invitations_token_hash', table_name='team_invitations')
    op.drop_index('ix_team_invitations_email_status', table_name='team_invitations')
    op.drop_index('ix_team_invitations_team_status', table_name='team_invitations')
    op.drop_table('team_invitations')
    op.drop_table('team_roster_eligibility')
    op.drop_table('team_duty_roles')
    op.drop_table('team_memberships')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
    op.drop_table('teams')
