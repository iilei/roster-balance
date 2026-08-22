"""Add roster lanes linked to rest rules."""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op  # type: ignore[attr-defined]

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = '004_roster_lanes'
down_revision: str | None = '003_rest_rules'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'roster_lanes',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('team_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('duration', sa.Integer(), nullable=False),
        sa.Column('rest_rule_id', sa.String(length=36), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(
            ['rest_rule_id'], ['rest_rules.id'], ondelete='RESTRICT'
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_roster_lanes_team_id', 'roster_lanes', ['team_id'])


def downgrade() -> None:
    op.drop_index('ix_roster_lanes_team_id', table_name='roster_lanes')
    op.drop_table('roster_lanes')
