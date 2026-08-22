from fastapi import FastAPI

from roster_balance.api.routes.availability_calendars import (
    router as availability_calendars_router,
)
from roster_balance.api.routes.me import router as me_router
from roster_balance.api.routes.member_favorability import (
    router as member_favorability_router,
)
from roster_balance.api.routes.rest_rules import router as rest_rules_router
from roster_balance.api.routes.roster_lanes import router as roster_lanes_router
from roster_balance.api.routes.team_duty_roles import router as team_duty_roles_router
from roster_balance.api.routes.team_eligibility import router as team_eligibility_router
from roster_balance.api.routes.team_invitations import router as team_invitations_router
from roster_balance.api.routes.team_owners import router as team_owners_router
from roster_balance.api.routes.teams import router as teams_router

app = FastAPI(
    title='RosterBalance',
    version='0.1.0',
    description='Explainable roster planning and decision service.',
)

app.include_router(teams_router)
app.include_router(availability_calendars_router)
app.include_router(me_router)
app.include_router(team_owners_router)
app.include_router(team_eligibility_router)
app.include_router(team_duty_roles_router)
app.include_router(member_favorability_router)
app.include_router(rest_rules_router)
app.include_router(roster_lanes_router)
app.include_router(team_invitations_router)


@app.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok'}
