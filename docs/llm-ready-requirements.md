# LLM-Ready Requirements: RosterBalance

Status: Early-stage implementation foundation
Date: 2026-08-22
Repository: roster-balance

## 1. Project objective

Build a service for creating, managing, validating, and explaining fair roster assignments for teams. The system must support:

- team and member management
- team ownership and membership authorization
- explicit roster eligibility separate from team membership
- availability calendars and time constraints
- declarative, explainable decision-making for roster planning
- PostgreSQL-backed persistence with Alembic migrations
- Dockerized local development and Lambda deployment compatibility

## 2. Current state summary

The project is structurally well-defined but not yet feature-complete.

### Verified project status

- Architecture and intent are documented in [README.md](../README.md), [docs/specification.md](specification.md), [docs/domain-model.md](domain-model.md), [docs/api.md](api.md), and [docs/decision-engine.md](decision-engine.md).
- The app entry point exists in [src/roster_balance/main.py](../src/roster_balance/main.py).
- The repo includes layered code organization under [src/roster_balance](../src/roster_balance): api, application, domain, infrastructure, and decision.
- Core services and route modules are scaffolded for team, invitation, ownership, eligibility, and related flows.
- Tooling is configured in [pyproject.toml](../pyproject.toml) and [mise.toml](../mise.toml).
- A thin health endpoint exists in the FastAPI app.

### Observed gaps

- The decision engine is not yet a complete production implementation.
- The persistence layer is not yet fully realized as a complete end-to-end domain implementation.
- The test suite is minimal and does not yet cover the core business flows or decision logic.
- [docs/architecture.md](architecture.md) is empty and should be filled in or replaced with a working architecture summary.
- The repo is best described as an architecture + skeleton foundation, not a finished product.

## 3. Hard architectural constraints

These constraints are mandatory and should be treated as non-negotiable requirements.

### Layer separation

- Keep domain logic independent from HTTP/API concerns.
- Keep application services responsible for orchestration.
- Keep infrastructure code responsible for AWS, DB, and external integrations.
- Keep decision-engine logic independent from datastore and HTTP concerns.

### Domain constraints

- Do not introduce AWS dependencies into domain or decision-engine code.
- Do not introduce database access into the decision engine.
- Do not add executable expressions to TOML policy configuration.
- Use Alembic migrations for schema changes.
- Preserve explainability of automated decisions.
- Prefer a small explicit implementation over premature abstraction.

### Team-modeling constraints

- Team membership must not imply roster eligibility.
- Team association/authorization roles are separate from roster eligibility.
- Adding a user to a team must not make them assignable by default.
- Team aliases should be short, human-friendly strings with a maximum length of 11 characters and a database-side uniqueness constraint so duplicate aliases are rejected.

### Invitation constraints

- Prefer POST /teams/{team_id}/invitations with email and role.
- Do not expose generic user/email search that allows enumeration or harvesting.
- Invitation responses should be generic; use rate limiting, expiration, single-use tokens, audit, and owner authorization.
- Local development should not send external emails; generate a preview artifact/tokenized output instead.
- Mailto links are only a convenience when the acceptance base URL is reachable by the recipient; not for localhost-only flows.

## 4. Functional requirements

### 4.1 Teams

Required behavior:

- Create, list, fetch, update, and delete teams.
- Support API-level team membership and ownership semantics.
- Require owner privileges for owner-sensitive actions.
- Prevent duplicate team names case-insensitively.
- Keep a team user relationship separate from eligibility.

### 4.2 Members and membership

Required behavior:

- Represent members with their own identity and properties.
- Associate members with teams through explicit team membership.
- Keep team membership and roster eligibility as distinct relations.
- Use owner-only team membership management and invitation-based onboarding flows.

### 4.3 Team eligibility

Required behavior:

- Allow explicit eligibility configuration per team and duty role.
- Only eligible members can be considered for assignment at planning time.
- Expose explicit collection and mutation APIs for eligible members.

### 4.4 Invitations

Required behavior:

- Owner-authenticated invitation creation by email.
- Single-use token flow with expiration.
- Generic response semantics to avoid user enumeration.
- Local preview generation without external email delivery.
- Acceptance creates membership only and does not add roster eligibility automatically.

### 4.5 Decision engine

Required behavior:

- Evaluate candidates using hard constraints, metrics, scoring rules, and deterministic tie-breaking.
- Return explainable outputs showing eligibility, rejections, weighted contributions, and selected candidate.
- Use a declared policy model and versioned configuration.
- Disallow arbitrary executable expressions in policy configuration.
- Keep the engine decoupled from data access and HTTP handling.

### 4.6 Persistence and schema

Required behavior:

- Use PostgreSQL as the primary persistence system.
- Use Alembic for schema migrations.
- Maintain clear mapping between domain models and persisted records.
- Keep application and decision logic independent from raw DB operations.

### 4.7 Calendar, scheduling, and policy semantics

The system must treat availability calendars, team calendars, and operational scheduling policies as distinct concepts.

Required behavior:

- Calendar URL paths must be resource-oriented; action names such as import must not appear in the route path.
- Member calendar uploads must accept VCF files through multipart form data and include an explicit effect field with values such as blocked or available.
- The initial source format must be vcard and remain extensible for future imports.
- A calendar record must use a globally unique calendar ID regardless of whether it belongs to a member, team, or instance-level scope.
- Team membership must not imply roster eligibility, and team ownership must not imply that a calendar is also a member calendar.
- The planner must resolve member, team, and instance calendars with explicit precedence and explain the precedence in the decision output.
- Team owners may maintain team-scoped fallback calendars when instance-level regional calendars are missing or stale.
- Work schedules, office hours, yellow-response hours, and red-response hours are operating policy resources, not imported holiday calendars.
- The default policy configuration must be team-agnostic and keyed by policy identity rather than team names.
- Time intervals must use start-inclusive, end-exclusive semantics.
- The default time precision for planning and policy rules should be minute-level; nanosecond precision is not required for roster planning.
- Exactly one calendar per calendar type per member scope must be enforceable, with duplicate creation rejected as a conflict.

## 5. API requirements

The intended API directions include:

- /teams
- /me
- /me/teams
- /teams/{team_id}/team-members
- /teams/{team_id}/eligible-members
- /teams/{team_id}/team-owners
- /teams/{team_id}/invitations
- /invitations/{invitation_id}/preview
- /invitations/{invitation_id}/accept
- roster lane and roster-related endpoints
- planning/validation/explain commands for roster decisions

The canonical naming preference is:

- /teams/{team_id}/team-members for team association/roles
- /teams/{team_id}/eligible-members for roster participation eligibility

This distinction is important and should not be collapsed into a single concept.

### Resource-oriented endpoint pattern

The following are the agreed calendar and scheduling endpoints for the first implementation milestone:

- POST /members/{member_id}/availability-calendars
- GET /members/{member_id}/availability-calendars
- GET /members/{member_id}/availability-calendars/{calendar_id}
- PUT /members/{member_id}/availability-calendars/{calendar_id}
- DELETE /members/{member_id}/availability-calendars/{calendar_id}
- POST /teams/{team_id}/calendars
- GET /teams/{team_id}/calendars
- GET /teams/{team_id}/calendars/{calendar_id}
- PUT /teams/{team_id}/calendars/{calendar_id}
- DELETE /teams/{team_id}/calendars/{calendar_id}
- POST /calendars
- GET /calendars
- GET /calendars/{calendar_id}
- PUT /calendars/{calendar_id}
- DELETE /calendars/{calendar_id}
- GET /work-schedules/default
- PUT /work-schedules/default
- GET /teams/{team_id}/work-schedule
- PUT /teams/{team_id}/work-schedule

The response payload for a created calendar record must return the globally unique calendar ID so the client can subsequently call PUT or DELETE using that ID.

The payload contract for file-based calendar import must support the following fields:

- name
- type
- custom_type when applicable
- effect
- source_format
- file
- optional metadata such as country, state, county, and span_from/span_to for instance or team calendars

## 6. Project delivery status by area

### Completed / present

- Repo scaffolding and structure
- Core architectural intent
- Domain vocabulary and modeling guidance
- Team-related service skeletons
- FastAPI app bootstrap and health endpoint
- Tooling and local dev commands

### Near-term implementation priorities

For the next milestone, the implementation should prioritize the following in order:

1. Team ownership and membership flows
   - complete team CRUD with owner-only authorization checks
   - enforce duplicate-name validation and explicit membership records
   - keep membership and eligibility as distinct relations

2. Explicit roster eligibility APIs
   - add the eligible-members resource model and update behavior
   - ensure planning and scoring only consider explicitly eligible members
   - preserve team membership and roster participation as separate concepts

3. Invitation lifecycle and onboarding
   - complete owner-authenticated invitation creation and acceptance flow
   - use single-use tokens, expiration, audit metadata, and generic responses
   - ensure acceptance grants membership but not implicit roster eligibility

4. Explainable decision engine
   - finish hard constraints, scoring, and deterministic ordering semantics
   - return ranked candidates, rejections, and contributing factors in output
   - keep policy configuration declarative and versioned without executable expressions

5. Calendar and scheduling foundations
   - implement resource-oriented calendar endpoints and VCF imports
   - enforce explicit calendar precedence and per-scope uniqueness rules
   - keep work schedules separate from imported holiday calendars

6. Persistence and verification
   - implement the required PostgreSQL persistence layer with Alembic migrations
   - add targeted integration and unit tests for each domain boundary
   - verify the app remains explainable and decoupled from infrastructure concerns

This milestone should produce a working, testable baseline for team membership, eligibility, invitation onboarding, and explainable roster planning without conflating authorization with roster assignment authority.

- Decision-engine conceptual design

### In progress

- Team ownership flow
- Eligibility flow
- Invitation flow
- Service implementations
- Integration with persistence
- Decision logic implementation

### Missing or incomplete

- Complete persistence layer
- Real business logic coverage
- Full validation for roster planning behavior
- Real decision-engine scoring implementation
- Complete test coverage for domain and integration behaviors
- Full documentation of architecture and infrastructure specifics

## 7. Acceptance criteria for next implementation milestone

The next milestone should be considered complete only when all of the following are true:

1. Team creation and ownership semantics work end-to-end.
2. Team membership and roster eligibility are fully separated.
3. Invitation flow works with generic responses and local preview artifacts.
4. Alembic migrations cover required schema changes.
5. Decision engine evaluates candidates using explicit constraints and explainable scoring.
6. Tests cover core domain behavior, not just placeholder assertions.
7. Project runs through the repo-managed workflow via Mise tasks.
8. No AWS or DB access leaks into domain or decision-engine code.

## 8. Recommended implementation order

1. Finish the domain model and persistence contracts.
2. Implement team membership and ownership services.
3. Implement explicit eligibility management.
4. Implement the invitation workflow and local delivery artifact.
5. Implement scheduling/availability models.
6. Implement decision policies and explainable scoring.
7. Add end-to-end tests covering real behavior.
8. Complete API docs and architecture docs.

## 9. Working summary for an LLM agent

Treat this as a greenfield but already-structured project with strong architectural intent. Do not broaden scope beyond the defined design. Keep domain, application, infrastructure, and decision concerns explicitly separated. Preserve explainability and explicit eligibility semantics. Prefer cloning the existing patterns in the repo over inventing a new architecture. Avoid adding AWS or database concerns to the decision engine, and avoid executable policy logic in TOML files.

## 10. Immediate instruction to any future agent

Before implementing new behavior:

- Read [README.md](../README.md)
- Read [docs/specification.md](specification.md)
- Read [docs/domain-model.md](domain-model.md)
- Read [docs/api.md](api.md)
- Read [docs/decision-engine.md](decision-engine.md)
- Read [.github/copilot-instructions.md](../.github/copilot-instructions.md) if present in the repo
- Keep DB, AWS, and HTTP concerns out of the domain and decision-engine layers
- Add or update tests for any domain behavior change
- Use Mise-managed commands for verification when available
