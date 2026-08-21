# RosterBalance Copilot Instructions

RosterBalance is a Python service for managing and planning explainable service rosters.

Authoritative architecture and domain documentation lives in `docs/`.

## Core rules

- Keep domain logic independent from HTTP, AWS and PostgreSQL.
- Do not put business rules into FastAPI routes.
- Do not put business rules into SQLAlchemy models or repository implementations.
- The decision engine must not query the database directly.
- The decision engine receives domain objects and a prepared decision context.
- PostgreSQL is the primary operational data store.
- S3 is not PostgreSQL storage; use it only for backups, exports, snapshots or audit artifacts.
- TOML is used for declarative decision / weighting policies.
- Never execute arbitrary code or `eval()` expressions from TOML.
- Hard constraints and weighted scoring factors must remain conceptually separate.
- Every decision should be explainable using machine-readable decision results.
- New domain rules require unit tests.
- Prefer explicit, readable implementations over clever abstractions.
- Keep AWS Lambda integration as an adapter around the HTTP application.
- Local development must remain possible with Docker Compose.
- Database schema changes must be represented by Alembic migrations.
- Do not silently violate hard constraints.
- If no valid candidate exists, return an explicit failure instead of making an invalid assignment.
- Use stable IDs instead of names as technical identifiers.
- Before changing domain behavior, read the relevant file in `docs/`.
