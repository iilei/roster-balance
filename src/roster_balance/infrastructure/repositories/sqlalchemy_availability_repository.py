"""SQLAlchemy-backed availability repositories."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import delete, select

from roster_balance.domain.models.availability import (
    AvailabilityCalendar,
    AvailabilityEntry,
)
from roster_balance.infrastructure.db.models import (
    AvailabilityCalendarModel,
    AvailabilityEntryModel,
)

if TYPE_CHECKING:
    import builtins

    from sqlalchemy.orm import Session, sessionmaker


class SQLAlchemyAvailabilityCalendarRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list_for_team(self, team_id: str) -> builtins.list[AvailabilityCalendar]:
        with self._session_factory.begin() as session:
            rows = session.scalars(
                select(AvailabilityCalendarModel).where(
                    AvailabilityCalendarModel.team_id == team_id
                )
            ).all()
            return [self._to_domain(row) for row in rows]

    def get(self, calendar_id: str) -> AvailabilityCalendar | None:
        with self._session_factory.begin() as session:
            row = session.get(AvailabilityCalendarModel, calendar_id)
            return None if row is None else self._to_domain(row)

    def add(self, calendar: AvailabilityCalendar) -> AvailabilityCalendar:
        with self._session_factory.begin() as session:
            row = AvailabilityCalendarModel(
                id=calendar.id,
                team_id=calendar.team_id,
                member_id=calendar.member_id,
                type=calendar.type,
                custom_type=calendar.custom_type,
                name=calendar.name,
                timezone=calendar.timezone,
                source_format=calendar.source_format,
                source_filename=calendar.source_filename,
                imported_at=calendar.imported_at,
                country=calendar.country,
                state=calendar.state,
                county=calendar.county,
                span_from=calendar.span_from,
                span_to=calendar.span_to,
                created_at=calendar.created_at,
                updated_at=calendar.updated_at,
            )
            session.add(row)
            session.flush()
            return self._to_domain(row)

    def delete(self, calendar_id: str) -> None:
        with self._session_factory.begin() as session:
            session.execute(
                delete(AvailabilityCalendarModel).where(
                    AvailabilityCalendarModel.id == calendar_id
                )
            )

    def save(self, calendar: AvailabilityCalendar) -> AvailabilityCalendar:
        with self._session_factory.begin() as session:
            row = session.get(AvailabilityCalendarModel, calendar.id)
            if row is None:
                raise LookupError(calendar.id)
            row.name = calendar.name
            row.timezone = calendar.timezone
            row.custom_type = calendar.custom_type
            row.source_format = calendar.source_format
            row.source_filename = calendar.source_filename
            row.imported_at = calendar.imported_at
            row.country = calendar.country
            row.state = calendar.state
            row.county = calendar.county
            row.span_from = calendar.span_from
            row.span_to = calendar.span_to
            row.updated_at = calendar.updated_at
            session.flush()
            return self._to_domain(row)

    @staticmethod
    def _to_domain(row: AvailabilityCalendarModel) -> AvailabilityCalendar:
        return AvailabilityCalendar(
            id=row.id,
            team_id=row.team_id,
            member_id=row.member_id,
            type=row.type,
            custom_type=row.custom_type,
            name=row.name,
            timezone=row.timezone,
            source_format=row.source_format,
            source_filename=row.source_filename,
            imported_at=row.imported_at,
            country=row.country,
            state=row.state,
            county=row.county,
            span_from=row.span_from,
            span_to=row.span_to,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )


class SQLAlchemyAvailabilityEntryRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list_for_calendar(self, calendar_id: str) -> builtins.list[AvailabilityEntry]:
        with self._session_factory.begin() as session:
            rows = session.scalars(
                select(AvailabilityEntryModel)
                .where(AvailabilityEntryModel.calendar_id == calendar_id)
                .order_by(AvailabilityEntryModel.starts_at)
            ).all()
            return [self._to_domain(row) for row in rows]

    def get(self, entry_id: str) -> AvailabilityEntry | None:
        with self._session_factory.begin() as session:
            row = session.get(AvailabilityEntryModel, entry_id)
            return None if row is None else self._to_domain(row)

    def add(self, entry: AvailabilityEntry) -> AvailabilityEntry:
        with self._session_factory.begin() as session:
            row = AvailabilityEntryModel(
                id=entry.id,
                calendar_id=entry.calendar_id,
                starts_at=entry.starts_at,
                ends_at=entry.ends_at,
                availability=entry.availability,
                reason=entry.reason,
                created_at=entry.created_at,
                updated_at=entry.updated_at,
            )
            session.add(row)
            session.flush()
            return self._to_domain(row)

    def add_many(self, entries: list[AvailabilityEntry]) -> list[AvailabilityEntry]:
        with self._session_factory.begin() as session:
            rows = [
                AvailabilityEntryModel(
                    id=entry.id,
                    calendar_id=entry.calendar_id,
                    starts_at=entry.starts_at,
                    ends_at=entry.ends_at,
                    availability=entry.availability,
                    reason=entry.reason,
                    created_at=entry.created_at,
                    updated_at=entry.updated_at,
                )
                for entry in entries
            ]
            session.add_all(rows)
            session.flush()
            return [self._to_domain(row) for row in rows]

    def save(self, entry: AvailabilityEntry) -> AvailabilityEntry:
        with self._session_factory.begin() as session:
            row = session.get(AvailabilityEntryModel, entry.id)
            if row is None:
                raise LookupError(entry.id)
            for field in (
                'starts_at',
                'ends_at',
                'availability',
                'reason',
                'updated_at',
            ):
                setattr(row, field, getattr(entry, field))
            session.flush()
            return self._to_domain(row)

    def delete(self, entry_id: str) -> None:
        with self._session_factory.begin() as session:
            session.execute(
                delete(AvailabilityEntryModel).where(
                    AvailabilityEntryModel.id == entry_id
                )
            )

    @staticmethod
    def _to_domain(row: AvailabilityEntryModel) -> AvailabilityEntry:
        return AvailabilityEntry(
            row.id,
            row.calendar_id,
            row.starts_at,
            row.ends_at,
            row.availability,
            row.reason,
            row.created_at,
            row.updated_at,
        )
