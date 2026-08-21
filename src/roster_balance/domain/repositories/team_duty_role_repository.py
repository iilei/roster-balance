"""Repository boundary for configured team duty roles."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    import builtins

    from roster_balance.domain.models.team_duty_role import TeamDutyRole


class TeamDutyRoleRepository(Protocol):
    def list_for_team(self, team_id: str) -> builtins.list[TeamDutyRole]: ...

    def get(self, role_id: str) -> TeamDutyRole | None: ...

    def get_by_slug(self, team_id: str, slug: str) -> TeamDutyRole | None: ...

    def add(self, role: TeamDutyRole) -> TeamDutyRole: ...

    def save(self, role: TeamDutyRole) -> TeamDutyRole: ...
