from fastapi import FastAPI

from roster_balance.api.routes.teams import router as teams_router
from roster_balance.infrastructure.repositories.in_memory_team_repository import (
    InMemoryTeamRepository,
)
from roster_balance.application.services.team_service import TeamService

app = FastAPI(
    title="RosterBalance",
    version="0.1.0",
    description="Explainable roster planning and decision service.",
)

team_service = TeamService(InMemoryTeamRepository())
app.include_router(teams_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
