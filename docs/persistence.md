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
