"""In-memory roster eligibility repository."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from roster_balance.domain.models.team_eligibility import TeamEligibility


class InMemoryTeamEligibilityRepository:
    def __init__(self) -> None:
        self._eligibility: dict[tuple[str, str, str], TeamEligibility] = {}

    def list_for_team(self, team_id: str) -> list[TeamEligibility]:
        return [
            relation
            for relation in self._eligibility.values()
            if relation.team_id == team_id
        ]

    def list_for_role(self, team_id: str, duty_role_id: str) -> list[TeamEligibility]:
        return [
            relation
            for relation in self._eligibility.values()
            if relation.team_id == team_id and relation.duty_role_id == duty_role_id
        ]

    def get(
        self, team_id: str, member_id: str, duty_role_id: str
    ) -> TeamEligibility | None:
        return self._eligibility.get((team_id, member_id, duty_role_id))

    def add(self, eligibility: TeamEligibility) -> TeamEligibility:
        self._eligibility[
            (eligibility.team_id, eligibility.member_id, eligibility.duty_role_id)
        ] = eligibility
        return eligibility

    def delete(self, team_id: str, member_id: str, duty_role_id: str) -> None:
        self._eligibility.pop((team_id, member_id, duty_role_id), None)
