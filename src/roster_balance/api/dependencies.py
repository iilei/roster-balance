"""FastAPI dependency wiring for the application layer."""

import os

from roster_balance.application.services.team_service import TeamService
from roster_balance.domain.team_ids import TeamIdSpace
from roster_balance.infrastructure.repositories.in_memory_team_repository import (
    InMemoryTeamRepository,
)

team_service = TeamService(
    InMemoryTeamRepository(),
    TeamIdSpace(
        maximum_teams=int(os.getenv("TEAM_MAXIMUM", "1000000")),
        seed=os.getenv("TEAM_ID_SEED", "local-development"),
    ),
)


def get_team_service() -> TeamService:
    return team_service
