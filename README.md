# RosterBalance

RosterBalance is a service for creating, managing, validating, and eventually planning
fair and explainable service rosters.

The project is intentionally designed around a clear separation of concerns:

- REST-like API for teams, members, availability calendars, roster lanes and rosters
- PostgreSQL as primary persistence
- Versioned, declarative decision policies with explainable scoring
- decision engine independent from database and HTTP concerns
- Docker-based local development
- deployable as a containerized AWS Lambda
- S3 only for backup / export / audit artifacts, not as PostgreSQL primary storage

## Architecture at a glance

```text
HTTP / FastAPI
      |
Application Services
      |
Domain Model
  |         |
  |         +--> Decision Engine
  |
Repository Interfaces
      |
SQLAlchemy / PostgreSQL
```

The Lambda adapter is infrastructure only. The application itself must remain runnable
without AWS-specific dependencies.

## Local development

```bash
docker compose up --build
```

To verify the API and its generated OpenAPI document:

```bash
mise run openapi
```

Then open `http://localhost:8000/docs` for Swagger UI or
`http://localhost:8000/openapi.json` for the raw schema.

Database schema changes are managed with Alembic:

```bash
alembic upgrade head
```

If PostgreSQL failed during its first initialization, remove the failed local
volume and start again:

```bash
docker compose down -v
mise run openapi
```

Expected services:

- `api`
- `postgres`

## Important documents

- `docs/specification.md`
- `docs/domain-model.md`
- `docs/api.md`
- `docs/decision-engine.md`
- `docs/persistence.md`
- `docs/deployment.md`
- `.github/copilot-instructions.md`
