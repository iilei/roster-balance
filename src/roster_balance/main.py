from fastapi import FastAPI

from roster_balance.api.routes.teams import router as teams_router

app = FastAPI(
    title="RosterBalance",
    version="0.1.0",
    description="Explainable roster planning and decision service.",
)

app.include_router(teams_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
