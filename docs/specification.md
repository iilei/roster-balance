# RosterBalance – Product and Architecture Specification

## Goal

RosterBalance is a service that manages team membership, member properties,
availability calendars and roster lanes and later supports explainable roster planning.

The service should be:

- easy to run locally
- cheap and maintainable to host in AWS
- deployable as a containerized Lambda
- REST-like
- backed primarily by PostgreSQL
- testable without AWS
- explainable in its planning decisions
- extensible through versioned, declarative decision policies

## Primary domain resources

- Team
- Member
- TeamMembership
- AvailabilityCalendar
- AvailabilityEntry
- MemberAvailabilityCalendar
- RosterLane
- Roster
- Assignment
- DecisionPolicy
- DecisionResult

## Key cardinalities

```text
Member 0..* <-> 0..* Team

Member 0..1 AvailabilityCalendar per calendar type

AvailabilityCalendar 1 -> 0..* AvailabilityEntry

Team 1 -> 0..* RosterLane

Team 1 -> 0..* Roster

Roster 1 -> 0..* Assignment
```

## Member properties

Initial examples:

- `avoidance_score`
- future extensible properties

The exact semantic range of scores must be documented and validated.

Recommended initial convention:

```text
0.0 = no avoidance preference
1.0 = strongest avoidance preference
```

## Availability calendar types

Initial types:

- `holiday`
- `vacation`
- `custom`

For custom calendars, use a separate `custom_type` field instead of encoding it into
a magic string.

Example:

```json
{
  "type": "custom",
  "customType": "training"
}
```

## Roster lane

A roster lane describes a category of service slots, for example:

- on-call
- remediation manager
- day service

Roster lanes describe what needs to be staffed. Decision policies describe how
candidates are evaluated.

## Roster

A roster represents a bounded planning period for one team.

Suggested states:

- `draft`
- `planned`
- `validated`
- `published`
- `closed`

## Assignment

An assignment binds:

- roster
- roster lane
- time range
- member

Suggested metadata:

- `source`: `manual`, `planner`, `import`
- `locked`: whether automated replanning may modify it

## Explainability

Automatic planning must expose why a member was chosen and why others were not.

A decision result should include:

- candidate eligibility
- violated hard constraints
- raw metric values
- weights
- weighted score contributions
- total score
- selected candidate
