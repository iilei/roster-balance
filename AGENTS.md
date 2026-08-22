# Agent Instructions

Before implementing a task:

1. Read `.github/skills/python-quality/copilot-instructions.md`.
2. Read the relevant files in `docs/`.
3. Keep domain, application and infrastructure layers separate.
4. Add or update tests for all domain behavior.
5. Do not introduce AWS dependencies into domain or decision-engine code.
6. Do not introduce database access into the decision engine.
7. Do not add executable expressions to TOML policy configuration.
8. Represent schema changes through Alembic migrations.
9. Preserve explainability of all automated decisions.
10. Prefer a small explicit implementation over premature abstraction.

Operational guidance:

- If a `mise.toml` file exists in the repo, prefer project-managed commands such as `mise run fmt` and related `mise run ...` tasks for formatting, linting, and tests before invoking tool-specific binaries directly.
- In other words, use the repo's configured Mise entrypoints as the default path for Ruff and similar checks rather than calling `ruff`, `pytest`, or other tools directly unless the task specifically requires it.
