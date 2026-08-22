"""Add availability calendar source metadata."""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op  # type: ignore[attr-defined]

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = '006_calendar_source_metadata'
down_revision: str | None = '005_availability_calendars'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('availability_calendars', sa.Column('source_format', sa.String(32)))
    op.add_column(
        'availability_calendars', sa.Column('source_filename', sa.String(255))
    )
    op.add_column(
        'availability_calendars',
        sa.Column('imported_at', sa.DateTime(timezone=True)),
    )
    op.add_column('availability_calendars', sa.Column('country', sa.String(100)))
    op.add_column('availability_calendars', sa.Column('state', sa.String(100)))
    op.add_column('availability_calendars', sa.Column('county', sa.String(100)))
    op.add_column(
        'availability_calendars',
        sa.Column('span_from', sa.DateTime(timezone=True)),
    )
    op.add_column(
        'availability_calendars',
        sa.Column('span_to', sa.DateTime(timezone=True)),
    )


def downgrade() -> None:
    for column in (
        'span_to',
        'span_from',
        'county',
        'state',
        'country',
        'imported_at',
        'source_filename',
        'source_format',
    ):
        op.drop_column('availability_calendars', column)
