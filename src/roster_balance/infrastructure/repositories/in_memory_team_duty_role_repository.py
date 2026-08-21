"""In-memory team duty-role repository."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from roster_balance.domain.models.team_duty_role import TeamDutyRole


class InMemoryTeamDutyRoleRepository:
    def __init__(self) -> None:
        self._roles: dict[str, TeamDutyRole] = {}

    def list_for_team(self, team_id: str) -> list[TeamDutyRole]:
        return [role for role in self._roles.values() if role.team_id == team_id]

    def get(self, role_id: str) -> TeamDutyRole | None:
        return self._roles.get(role_id)

    def get_by_slug(self, team_id: str, slug: str) -> TeamDutyRole | None:
        return next(
            (role for role in self.list_for_team(team_id) if role.slug == slug),
            None,
        )

    def add(self, role: TeamDutyRole) -> TeamDutyRole:
        self._roles[role.id] = role
        return role

    def save(self, role: TeamDutyRole) -> TeamDutyRole:
        self._roles[role.id] = role
        return role
