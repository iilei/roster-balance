# Persistence Strategy

## Primary choice

PostgreSQL is the primary operational datastore.

Reasons:

- natural fit for many-to-many team memberships
- strong uniqueness constraints
- useful relational queries for historical load and fairness
- good fit for reporting
- familiar migration tooling
- personal preference and maintainability

## Python stack

Recommended:

- SQLAlchemy 2
- Alembic
- psycopg
- PostgreSQL

## Repository boundary

```text
Application Services
       |
Repository Interfaces
       |
SQLAlchemy Repository Implementations
       |
PostgreSQL
```

Domain code should not depend on SQLAlchemy.

## Initial relational model

```text
teams
members
team_memberships
team_duty_roles
team_roster_eligibility
availability_calendars
member_availability_calendars
availability_entries
roster_lanes
rosters
assignments
```

Important invariant:

```sql
UNIQUE (member_id, calendar_type)
```

Duty-role configuration and eligibility are separate relations:

```text
team_duty_roles
- id
- team_id
- slug
- display_name
- description
- active
- created_at
- updated_at
- UNIQUE (team_id, slug)

team_roster_eligibility
- team_id
- member_id
- duty_role_id
- duty_role
- created_at
- UNIQUE (team_id, member_id, duty_role_id)
```

Eligibility writes must verify in the application transaction that the member
belongs to the team and the duty role belongs to that team and is active.

for the member-to-availability-calendar relation.

## S3

S3 should NOT be used as PostgreSQL primary storage.

Good uses:

- database backups
- exports
- published roster snapshots
- immutable decision traces
- audit artifacts
- large historical artifacts if required later

Conceptual split:

```text
PostgreSQL:
- teams
- members
- memberships
- calendars
- current and historical rosters
- assignments

S3:
- backups
- exports
- immutable snapshots
- optional audit archives
```

## Local Docker data

The local PostgreSQL service uses the named Docker volume
`roster_balance_postgres`, mounted at `/var/lib/postgresql` for PostgreSQL 18.
Stopping or recreating containers does not remove this volume, so records survive
both of these workflows:

```bash
docker compose stop
docker compose start

docker compose down
docker compose up
```

To deliberately discard the local database, including all records, run:

```bash
docker compose down -v
```

The local database is disposable development state. Production data requires
PostgreSQL backups and a recovery procedure; Docker volumes are not a backup.

Invitation expiry is configured system-wide with `INVITATION_TTL_HOURS` (default
`4`). Resend attempts are controlled independently by
`INVITATION_RESEND_COOLDOWN_MINUTES` (default `15`). The application treats the
TTL as the lifetime of a pending invitation, not as a resend permission.
Expired pending invitations are removed by a vacuum operation; terminal
invitations are retained for audit. The local in-memory adapter runs this vacuum
lazily on invitation creation and exposes it as an application operation. A
PostgreSQL deployment should run the same cleanup from a scheduled worker or
maintenance job.
