"""SQLAlchemy-backed rest-rule repository."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import delete, select

from roster_balance.domain.models.rest_rule import RestRule
from roster_balance.infrastructure.db.models import RestRuleModel

if TYPE_CHECKING:
    import builtins

    from sqlalchemy.orm import Session, sessionmaker


class SQLAlchemyRestRuleRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list_for_team(self, team_id: str) -> builtins.list[RestRule]:
        with self._session_factory.begin() as session:
            rows = session.scalars(
                select(RestRuleModel)
                .where(RestRuleModel.team_id == team_id)
                .order_by(RestRuleModel.created_at)
            ).all()
            return [self._to_domain(row) for row in rows]

    def get(self, rule_id: str) -> RestRule | None:
        with self._session_factory.begin() as session:
            row = session.get(RestRuleModel, rule_id)
            return None if row is None else self._to_domain(row)

    def add(self, rule: RestRule) -> RestRule:
        with self._session_factory.begin() as session:
            row = RestRuleModel(
                id=rule.id,
                team_id=rule.team_id,
                name=rule.name,
                cooldown_after=rule.cooldown_after,
                active=rule.active,
                created_at=rule.created_at,
                updated_at=rule.updated_at,
            )
            session.add(row)
            session.flush()
            return self._to_domain(row)

    def save(self, rule: RestRule) -> RestRule:
        with self._session_factory.begin() as session:
            row = session.get(RestRuleModel, rule.id)
            if row is None:
                raise LookupError(rule.id)
            row.name = rule.name
            row.cooldown_after = rule.cooldown_after
            row.active = rule.active
            row.updated_at = rule.updated_at
            session.flush()
            return self._to_domain(row)

    def delete(self, rule_id: str) -> None:
        with self._session_factory.begin() as session:
            session.execute(delete(RestRuleModel).where(RestRuleModel.id == rule_id))

    @staticmethod
    def _to_domain(row: RestRuleModel) -> RestRule:
        return RestRule(
            id=row.id,
            team_id=row.team_id,
            name=row.name,
            cooldown_after=row.cooldown_after,
            active=row.active,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
