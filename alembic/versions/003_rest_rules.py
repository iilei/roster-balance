"""Add team-owned rest rules."""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op  # type: ignore[attr-defined]

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = '003_rest_rules'
down_revision: str | None = '002_member_favorability'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'rest_rules',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('team_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('cooldown_after', sa.Integer(), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_rest_rules_team_id', 'rest_rules', ['team_id'])


def downgrade() -> None:
    op.drop_index('ix_rest_rules_team_id', table_name='rest_rules')
    op.drop_table('rest_rules')
