"""Add team member availability calendars and entries."""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op  # type: ignore[attr-defined]

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = '005_availability_calendars'
down_revision: str | None = '004_roster_lanes'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'availability_calendars',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('team_id', sa.String(length=36), nullable=False),
        sa.Column('member_id', sa.String(length=255), nullable=False),
        sa.Column('type', sa.String(length=32), nullable=False),
        sa.Column('custom_type', sa.String(length=200), nullable=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('timezone', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['member_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'team_id',
            'member_id',
            'type',
            name='uq_availability_calendar_member_type',
        ),
    )
    op.create_table(
        'availability_entries',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('calendar_id', sa.String(length=36), nullable=False),
        sa.Column('starts_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('ends_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('availability', sa.String(length=32), nullable=False),
        sa.Column('reason', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['calendar_id'], ['availability_calendars.id'], ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'ix_availability_entries_calendar_starts',
        'availability_entries',
        ['calendar_id', 'starts_at'],
    )


def downgrade() -> None:
    op.drop_index(
        'ix_availability_entries_calendar_starts',
        table_name='availability_entries',
    )
    op.drop_table('availability_entries')
    op.drop_table('availability_calendars')
