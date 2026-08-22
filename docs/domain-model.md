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

Team IDs are database-generated UUIDs. They are the canonical internal
identifiers used for persistence, relationships, and route paths. The proquint
implementation remains available as a user-facing alias feature for scrubbed
output and human-friendly random labels, but it is not the system’s technical
identifier.

## User

```text
User
- id
- provider
- subject
- email
- display_name
- active
- created_at
- updated_at
```

`provider` and `subject` identify the external principal. The application user
ID is derived from that identity for the local implementation and is intended
to become a separately persisted application key when PostgreSQL identity
bindings are added.

## RosterTeamMembership

```text
TeamMembership
- team_id
- user_id
- role: owner | member
- created_at
```

This is the organizational association and authorization relation. Creating a
team creates its first membership with the `owner` role for the current user.
Only an existing owner may change roles, and at least one owner must remain.

## RosterEligibility

```text
RosterEligibility
- team_id
- member_id
- duty_role_id
- duty_role
- created_at
```

Team membership does not imply roster eligibility. Eligibility is an explicit
allowlist of roster participants used by planning.

Eligibility is scoped to a configured team duty role. A member may be eligible
for multiple roles, and team membership alone does not grant eligibility.

## TeamDutyRole

```text
TeamDutyRole
- id
- team_id
- slug
- display_name
- description
- active
- created_at
- updated_at
```

Duty roles are declarative team configuration. Their slugs form the namespace
used by the eligible-members API.

## TeamInvitation

```text
TeamInvitation
- id
- team_id
- inviter_user_id
- email
- role: member
- status: pending | accepted | declined | expired
- token_hash
- created_at
- expires_at
- accepted_at
- accepted_by_user_id
```

Invitation tokens are generated randomly, stored only as hashes, expire, and may
be accepted once. An accepted invitation creates organizational team membership;
roster eligibility remains a separate explicit relation.

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
- duration
- cooldown_after
- active
- created_at
- updated_at
```

A lane describes a staffing obligation, not the scoring policy itself. Its
`duration` is the length of an assignment and `cooldown_after` is the recovery
period required for the assigned member before another assignment may begin.
The cooldown is measured from the previous assignment's `ends_at` and uses a
start-inclusive, end-exclusive boundary: a candidate is eligible at exactly
`previous.ends_at + cooldown_after`.

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
