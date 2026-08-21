# REST-like API

This is an initial resource model, not a frozen OpenAPI contract. The generated
OpenAPI document is available at `/openapi.json`, and interactive Swagger UI is
available at `/docs` when the local API is running.

## Teams

```text
GET    /teams
POST   /teams
GET    /teams/{team_id}
PATCH  /teams/{team_id}
DELETE /teams/{team_id}
```

The collection endpoint supports case-insensitive substring search across team
names and descriptions:

```text
GET /teams?q=platform
```

Search returns the normal team list shape and returns `200 []` when there are no
matches. An omitted `q` returns all teams.

Team IDs are strings in the Proquint format. They are generated from a bounded
numeric slot space after a seeded Feistel permutation. `TEAM_MAXIMUM` controls
the maximum number of slots and therefore the fixed ID length; `TEAM_ID_SEED`
must remain stable for an environment.

## Identity and ownership

`GET /me` returns the normalized application user for the current principal.
Local Compose runs with `AUTHENTICATION_MODE=local` and resolves the deterministic
principal `local:dev`; it does not require an authorization header. Cloud mode
will resolve a Cognito principal supplied by the API Gateway authorizer.

Creating a team makes the current user its first owner. Owners can add or remove
other team members through:

```text
GET    /teams/{team_id}/team-members?role=owner
DELETE /teams/{team_id}/team-members/{user_id}
```

The collection supports owner-authorized removal of an existing team member.
Invitations are the only public way to add a new team member, preventing callers
from enumerating users or inventing membership IDs.

Team association does not imply roster eligibility. Owners manage eligibility
separately:

```text
GET    /teams/{team_id}/eligible-members
GET    /teams/{team_id}/eligible-members/{duty_role}
POST   /teams/{team_id}/eligible-members/{duty_role}
DELETE /teams/{team_id}/eligible-members/{duty_role}/{member_id}
```

Only eligible members may be considered for roster assignments.

## Invitations

Owners invite people by email rather than searching a public user directory:

```text
POST /teams/{team_id}/invitations
POST /invitations/{invitation_id}/accept
```

Invitation creation accepts an email address and returns a generic `202 Accepted`
response. It must not reveal whether the address already belongs to a user. The
invitation token is single-use and expires after the system-wide
`INVITATION_COOLDOWN_HOURS` period, which defaults to 4 hours. Expired pending
invitations are automatically vacuumed when the invitation service is accessed;
accepted and declined invitations remain available for audit. Acceptance creates
a `team-member` association only; it does not add roster eligibility.

### Team membership

```text
GET    /teams/{team_id}/team-members
```

## Members

```text
GET    /members
POST   /members
GET    /members/{member_id}
PATCH  /members/{member_id}
DELETE /members/{member_id}

GET    /members/{member_id}/teams
```

## Member availability calendars

```text
GET    /members/{member_id}/availability-calendars
PUT    /members/{member_id}/availability-calendars/{calendar_type}
DELETE /members/{member_id}/availability-calendars/{calendar_type}
```

Using the calendar type in the path makes the "maximum one calendar per type"
domain invariant visible at API level.

## Availability calendars

```text
GET    /availability-calendars
POST   /availability-calendars
GET    /availability-calendars/{calendar_id}
PATCH  /availability-calendars/{calendar_id}
DELETE /availability-calendars/{calendar_id}

GET    /availability-calendars/{calendar_id}/entries
POST   /availability-calendars/{calendar_id}/entries
PATCH  /availability-calendars/{calendar_id}/entries/{entry_id}
DELETE /availability-calendars/{calendar_id}/entries/{entry_id}
```

## Roster lanes

```text
GET    /roster-lanes
POST   /roster-lanes
GET    /roster-lanes/{lane_id}
PATCH  /roster-lanes/{lane_id}
DELETE /roster-lanes/{lane_id}
```

## Rosters

```text
GET    /rosters
POST   /rosters
GET    /rosters/{roster_id}
PATCH  /rosters/{roster_id}
DELETE /rosters/{roster_id}
```

## Assignments

```text
GET    /rosters/{roster_id}/assignments
POST   /rosters/{roster_id}/assignments
PATCH  /rosters/{roster_id}/assignments/{assignment_id}
DELETE /rosters/{roster_id}/assignments/{assignment_id}
```

## Commands

Not every interaction needs to be CRUD.

```text
POST /rosters/{roster_id}/validate
POST /rosters/{roster_id}/plan
POST /rosters/{roster_id}/explain
```

Potential future endpoint:

```text
POST /rosters/{roster_id}/slots/{slot_id}/candidates
```

This may return all candidates and their full explainable score breakdown.
