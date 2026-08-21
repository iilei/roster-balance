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

### Team membership

```text
GET    /teams/{team_id}/members
PUT    /teams/{team_id}/members/{member_id}
DELETE /teams/{team_id}/members/{member_id}
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
