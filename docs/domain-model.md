# Domain Model

## Team

```text
Team
- id
- name
- description
- active
- created_at
- updated_at
```

Team IDs are stable, human-readable Proquint strings generated from a bounded
numeric team slot. A seeded Feistel permutation maps slots before encoding them.
The configured maximum team count determines the numeric domain and the fixed
number of Proquint groups. The seed must remain stable for the lifetime of an
environment; it is configuration, not a per-request value.

## Member

```text
Member
- id
- display_name
- active
- avoidance_score
- created_at
- updated_at
```

## TeamMembership

Many-to-many relation between Member and Team.

```text
TeamMembership
- team_id
- member_id
- active
- optional membership-specific properties
- created_at
```

Do not store team IDs directly as an array on Member.

## AvailabilityCalendar

```text
AvailabilityCalendar
- id
- type: holiday | vacation | custom
- custom_type: nullable
- name
- timezone
```

## MemberAvailabilityCalendar

Explicit association between a member and a calendar.

Invariant:

```text
At most one calendar per member and calendar type.
```

This should be represented as a database uniqueness constraint where possible.

## AvailabilityEntry

```text
AvailabilityEntry
- id
- calendar_id
- starts_at
- ends_at
- availability
- reason
```

Possible future values for `availability`:

- `available`
- `unavailable`
- `preferred`
- `avoid`

## RosterLane

```text
RosterLane
- id
- team_id
- name
- active
- optional metadata
```

A lane describes a staffing dimension, not the scoring policy itself.

## Roster

```text
Roster
- id
- team_id
- starts_on
- ends_on
- status
```

## Assignment

```text
Assignment
- id
- roster_id
- lane_id
- member_id
- starts_at
- ends_at
- source
- locked
```

## Decision engine boundary

The decision engine operates only on domain models and prepared contexts.

It must not:

- open database sessions
- execute SQL
- call AWS APIs
- read FastAPI request objects
