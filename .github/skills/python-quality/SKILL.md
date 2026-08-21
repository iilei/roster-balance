---
name: python-quality
description: "Use when writing or repairing Python code in this repository, especially Ruff, mypy, pytest, FastAPI annotations, import classification, or pre-commit failures. Prevent class-scope annotation collisions, missing type-checking imports, isolated-hook dependency errors, and unsafe lint allowlists."
user-invocable: true
disable-model-invocation: false
---

# Python Quality

## When to Use

- Adding or changing Python modules, protocols, services, routes, or tests.
- Repairing `ruff`, `mypy`, `pytest`, or `prek` failures.
- Adding annotations inside classes that define methods named `list`, `dict`, or another built-in.
- Working with FastAPI dependency annotations.
- Updating pre-commit or Hatch/Mise quality tasks.

## Procedure

1. Read the repository instructions and the relevant domain documentation before changing behavior.
2. Inspect the current file after any formatter or automated edit. Preserve unrelated user changes.
3. Make the smallest edit that addresses the reported failure.
4. Run diagnostics on the touched files immediately after editing, then run the narrowest available test or quality command.
5. Do not claim tests passed unless the command actually returned a result.

## Annotation and Import Rules

- Add `from __future__ import annotations` to modules with forward references or class-level annotations that may be evaluated during class creation.
- Inside a class, a method named `list` shadows the built-in name for later annotations. Prefer an explicit method name such as `list_teams`; if the public method must remain `list`, annotate with `builtins.list[...]`.
- If `builtins` is used only in annotations, import it inside `if TYPE_CHECKING:`. Keep application and domain model imports used only by annotations in the same block.
- Use `TYPE_CHECKING` imports only when postponed annotations make the import unnecessary at runtime. Do not move imports that are required to construct runtime values or execute code.
- Use `typing.Annotated` for FastAPI dependencies and parameter metadata, for example `Annotated[str | None, Query(...)]` and `Annotated[Service, Depends(...)]`.
- Return the declared Pydantic response type from FastAPI handlers. Convert domain dataclasses explicitly with `ResponseModel.model_validate(...)` and use `from_attributes=True` when needed.

## Ruff Policy

- Fix correctness and architecture findings such as `F821`, `PLC0415`, `FAST002`, and invalid type annotations.
- Keep stylistic exceptions narrow. In this repository, `EM101` and `TRY003` may be globally ignored only when the project has explicitly chosen that policy.
- Scope test-only exceptions such as `INP001`, `S101`, and `PLR2004` to `tests/**/*.py`; never suppress them globally for application code.
- Do not use `--unsafe-fixes` merely to make a hook green without reviewing every resulting change.

## Mypy and Pre-commit

- Pre-commit hooks run in isolated environments. A mypy hook must declare every third-party package imported by files it checks in `additional_dependencies`, including `fastapi`, `pydantic`, and `pytest`.
- Keep project dependency constraints consistent across `project.optional-dependencies`, dependency groups, and hook dependencies where all are maintained.
- Regenerate `uv.lock` with `uv lock`; never hand-edit the lockfile.
- For Starlette's current TestClient compatibility, use the project dependency `httpx` and refresh the environment after changing dependency declarations. `httpx2` is a maintained successor in the broader ecosystem, but this project should not adopt it as a replacement unless the FastAPI/Starlette compatibility layer is intentionally migrated and revalidated together.

## Tests

- Use pytest assertions in test modules. If Ruff emits `S101`, allow it only for `tests/**/*.py`.
- Add unit tests for domain/application invariants and focused integration tests for HTTP/OpenAPI behavior.
- Include regression tests for collection-time import errors when annotation evaluation can fail.
- Run, as applicable:

```text
mise run fmt
mise run typecheck
pytest -q <focused-test-files>
```

- If runtime execution is unavailable, report that clearly and rely on static diagnostics only.

## Architecture Constraints

- Keep domain logic independent of FastAPI, AWS, SQLAlchemy, and PostgreSQL.
- Keep business rules in application/domain services rather than routes or ORM models.
- Keep authentication provider details at the API/infrastructure boundary.
- Represent schema changes with Alembic migrations.
- Preserve explainability of automated decisions.
