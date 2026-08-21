"""Repository boundary for roster eligibility."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    import builtins

    from roster_balance.domain.models.team_eligibility import TeamEligibility


class TeamEligibilityRepository(Protocol):
    def list_for_team(self, team_id: str) -> builtins.list[TeamEligibility]: ...

    def get(self, team_id: str, member_id: str) -> TeamEligibility | None: ...

    def add(self, eligibility: TeamEligibility) -> TeamEligibility: ...

    def delete(self, team_id: str, member_id: str) -> None: ...
