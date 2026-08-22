# LLM-Ready Requirements: RosterBalance

Status: Early-stage implementation foundation
Date: 2026-08-22
Repository: roster-balance

## 1. Objective

Build an explainable roster-planning service for team scheduling, membership management, eligibility controls, and operational policy enforcement.

The system must support:

- [ ] team and member management
- [x] owner/member authorization boundaries
- [x] explicit roster eligibility separate from team membership
- [ ] availability calendars and time constraints
- [ ] versioned, declarative decision policies
- [ ] PostgreSQL persistence with Alembic migrations
- [x] local Docker development and Lambda-compatible deployment

## 2. Current repo status

This repository is a structured foundation rather than a complete production implementation.

Present:

- [x] layered application structure: API, application, domain, infrastructure, and decision engine
- [x] FastAPI bootstrap and health endpoint
- [x] team, ownership, invitation, and eligibility service scaffolds
- [x] project tooling and local workflow configuration
- [x] core design docs for architecture, domain model, API, and decision engine
- [x] compact factoring-entity duration parsing with canonical integer-second normalization
- [x] owner-managed team-scoped availability calendars and availability entries
- [x] minimal iCalendar VEVENT parsing with an explicit availability effect

Gaps:

- [ ] decision engine not yet complete
- [ ] persistence layer not fully implemented end-to-end
- [ ] limited business-logic test coverage
- [ ] architecture docs still incomplete in places

## 3. Hard constraints

These are mandatory and non-negotiable:

- [x] Keep domain logic independent from HTTP, AWS, and database concerns.
- [x] Keep application services responsible for orchestration.
- [x] Keep infrastructure code responsible for AWS, DB, and external integrations.
- [x] Keep the decision engine independent from datastore and HTTP code.
- [x] Do not add AWS dependencies to the domain or decision engine.
- [x] Do not add database access to the decision engine.
- [x] Do not add executable expressions to TOML policy configuration.
- [x] Use Alembic migrations for schema changes.
- [x] Preserve explainability of all automated decisions.
- [x] Prefer small, explicit implementations over premature abstraction.

### Team-modeling constraints

- [x] Team membership must not imply roster eligibility.
- [x] Team association and owner/member roles are separate from roster eligibility.
- [x] Adding a user to a team must not make them assignable by default.
- [ ] Team aliases must be short, human-friendly strings with a maximum length of 11 characters.
- [ ] Team aliases require a database-side uniqueness constraint so duplicate aliases are rejected.

### Invitation constraints

- [x] Prefer POST /teams/{team_id}/invitations with email and role.
- [x] Do not expose generic user/email search that enables harvesting.
- [ ] Invitation responses should be generic; use rate limiting, expiration, single-use tokens, audit, and owner authorization.
- [x] Local development must not send external emails; generate a preview artifact or tokenized output instead.
- [ ] Mailto links are allowed only when the acceptance base URL is reachable by the recipient.

## 4. Functional requirements

### Teams

- [x] Create, list, fetch, update, and delete teams.
- [x] Support owner-only administrative actions.
- [x] Prevent duplicate team names case-insensitively.
- [x] Keep membership and eligibility as separate relations.

### Members and membership

- [ ] Represent members with a durable identity and properties.
- [x] Associate members with teams via explicit membership records.
- [x] Keep team membership and roster eligibility distinct.
- [x] Use owner-only membership management and invitation-based onboarding.

### Team eligibility

- [x] Allow explicit eligibility configuration per team and duty role.
- [x] Only explicitly eligible members can be considered in roster planning.
- [x] Expose explicit APIs for listing and mutating eligible members.

### Invitations

- [x] Owner-authenticated invitation creation by email.
- [x] Single-use token flow with expiration.
- [x] Generic response semantics to avoid user enumeration.
- [x] Local preview generation without external email delivery.
- [x] Acceptance creates membership only; it does not imply roster eligibility.

### Decision engine

- [x] Evaluate candidates using hard constraints, metrics, scoring rules, and deterministic tie-breaking.
- [x] Return explainable results showing eligibility, rejection reasons, raw values, weights, and selected candidate.
- [ ] Use a declared policy model and versioned configuration.
- [x] Keep the engine decoupled from data access and HTTP handling.
- [x] Apply an explicit cooldown constraint using prior assignment end times and lane cooldown values.

### Persistence and schema

- [ ] Use PostgreSQL as the primary persistence system.
- [x] Use Alembic for schema migrations.
- [ ] Maintain clear mapping between domain models and persisted records.
- [x] Keep application and decision logic independent from raw DB operations.

### Calendar, scheduling, and policy semantics

- [x] Factoring-entity duration input accepts strict `w`, `d`, `h`, and `m` tokens and normalizes to integer seconds.
- [x] Factoring-entity duration limits are configurable through `MAX_FACTORING_ENTITY_DURATION_SECONDS` at the API boundary.
- [x] Resource-oriented calendar URLs are required; action names such as import must not appear in the route path.
- [x] Calendar types and availability effects are validated at the application boundary.
- [x] Calendar type uniqueness per team member is enforced in the application and database model.
- [x] Member calendar uploads must accept iCalendar files with an explicit effect field such as blocked or available.
- [x] The domain can parse iCalendar VEVENT entries with an explicit `available` or `unavailable` effect.
- [ ] The initial source format should be icalendar and remain extensible.
- [ ] Calendar records must use a globally unique ID regardless of scope.
- [ ] Team membership, team ownership, and member calendar ownership are distinct concepts.
- [ ] The planner must resolve member, team, and instance calendars with explicit precedence and explain that precedence in the decision output.
- [ ] Team owners may maintain team-scoped fallback calendars when instance-level calendars are missing or stale.
- [ ] Work schedules and operating policies are distinct from imported holiday or availability calendars.
- [ ] Default policies must be team-agnostic and keyed by policy identity rather than team names.
- [ ] Time intervals must use start-inclusive, end-exclusive semantics.
- [ ] Minute-level precision is the default expectation for planning and policy rules.
- [ ] Exactly one calendar per calendar type per scope must be enforceable; duplicates must be rejected as a conflict.

## 5. API requirements

Canonical resources:

- [x] /teams
- [x] /me
- [x] /me/teams
- [x] /teams/{team_id}/team-members
- [x] /teams/{team_id}/eligible-members
- [x] /teams/{team_id}/team-owners
- [x] /teams/{team_id}/invitations
- [x] /invitations/{invitation_id}/preview
- [x] /invitations/{invitation_id}/accept
- [ ] roster lane and roster-related endpoints
- [ ] planning / validation / explain endpoints for roster decisions

Canonical naming preference:

- [x] /teams/{team_id}/team-members for team association and roles
- [x] /teams/{team_id}/eligible-members for roster participation eligibility

Rest-rule resources:

- [x] /teams/{team_id}/rest-rules
- [x] /teams/{team_id}/rest-rules/{rest_rule_id}

Resource-oriented calendar endpoints:

- [ ] POST /members/{member_id}/availability-calendars
- [ ] GET /members/{member_id}/availability-calendars
- [ ] GET /members/{member_id}/availability-calendars/{calendar_id}
- [ ] PUT /members/{member_id}/availability-calendars/{calendar_id}
- [ ] DELETE /members/{member_id}/availability-calendars/{calendar_id}
- [ ] POST /teams/{team_id}/calendars
- [ ] GET /teams/{team_id}/calendars
- [ ] GET /teams/{team_id}/calendars/{calendar_id}
- [ ] PUT /teams/{team_id}/calendars/{calendar_id}
- [ ] DELETE /teams/{team_id}/calendars/{calendar_id}
- [x] POST /teams/{team_id}/availability-calendars
- [x] GET /teams/{team_id}/availability-calendars
- [x] GET /teams/{team_id}/availability-calendars/{calendar_id}
- [x] PATCH /teams/{team_id}/availability-calendars/{calendar_id}
- [x] DELETE /teams/{team_id}/availability-calendars/{calendar_id}
- [x] GET /teams/{team_id}/availability-calendars/{calendar_id}/entries
- [x] POST /teams/{team_id}/availability-calendars/{calendar_id}/entries
- [x] PATCH /teams/{team_id}/availability-calendars/{calendar_id}/entries/{entry_id}
- [x] DELETE /teams/{team_id}/availability-calendars/{calendar_id}/entries/{entry_id}
- [x] POST /teams/{team_id}/availability-calendars/{calendar_id}/sources
- [ ] POST /calendars
- [ ] GET /calendars
- [ ] GET /calendars/{calendar_id}
- [ ] PUT /calendars/{calendar_id}
- [ ] DELETE /calendars/{calendar_id}
- [ ] GET /work-schedules/default
- [ ] PUT /work-schedules/default
- [ ] GET /teams/{team_id}/work-schedule
- [ ] PUT /teams/{team_id}/work-schedule

Calendar import payloads must support:

- [ ] name
- [ ] type
- [ ] custom_type when applicable
- [ ] effect
- [ ] source_format
- [ ] file
- [ ] optional metadata such as country, state, county, and span_from/span_to

## 6. Implementation priorities

The next milestone should prioritize these in order:

1. [x] Team ownership and membership flows
2. [x] Explicit roster eligibility APIs
3. [x] Invitation lifecycle and onboarding
4. [x] Explainable decision engine
5. [x] Rest rules and roster-lane configuration
6. [ ] Calendar and scheduling foundations
7. [ ] Persistence and verification

## 7. Acceptance criteria

The next milestone is complete only when:

1. [ ] Team creation and ownership semantics work end-to-end.
2. [x] Team membership and roster eligibility are fully separated.
3. [x] Invitation flow works with generic responses and local preview artifacts.
4. [ ] Alembic migrations cover the required schema changes.
5. [x] Decision engine evaluates candidates with explicit constraints and explainable scoring.
6. [ ] Core domain behavior is covered by real tests.
7. [x] The project runs through the repo-managed Mise workflow.
8. [x] No AWS or DB concerns leak into the domain or decision-engine code.

## 9. Suggested next step

Add member-scoped calendar associations and calendar source metadata, then add
PostgreSQL-backed integration tests. Follow that with calendar precedence in
the decision context and the availability hard constraint.

## 8. Agent guidance

Before implementing new behavior:

- Read [README.md](../README.md)
- Read [docs/specification.md](specification.md)
- Read [docs/domain-model.md](domain-model.md)
- Read [docs/api.md](api.md)
- Read [docs/decision-engine.md](decision-engine.md)
- Read [.github/copilot-instructions.md](../.github/copilot-instructions.md) if present
- Keep DB, AWS, and HTTP concerns out of the domain and decision-engine layers
- Add or update tests for any domain behavior change
- Use Mise-managed commands for verification when available
