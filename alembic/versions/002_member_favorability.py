"""Add member favorability configuration."""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op  # type: ignore[attr-defined]

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = '002_member_favorability'
down_revision: str | None = '001_initial_schema'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'member_favorability',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('team_id', sa.String(length=36), nullable=False),
        sa.Column('member_id', sa.String(length=255), nullable=False),
        sa.Column('duty_role_id', sa.String(length=36), nullable=False),
        sa.Column('effect', sa.String(length=32), nullable=False),
        sa.Column('blocking_level', sa.String(length=16), nullable=True),
        sa.Column('favorability', sa.Float(), nullable=True),
        sa.Column('constraint_strength', sa.Float(), nullable=True),
        sa.Column('source', sa.String(length=32), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['team_id', 'member_id'],
            ['team_memberships.team_id', 'team_memberships.user_id'],
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['duty_role_id'], ['duty_roles.id'], ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'team_id',
            'member_id',
            'duty_role_id',
            name='uq_member_favorability_member_role',
        ),
    )


def downgrade() -> None:
    op.drop_table('member_favorability')
