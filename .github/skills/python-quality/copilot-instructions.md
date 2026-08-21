# Python Type Checking Imports

For imports used only in annotations, add postponed annotations and place the
imports in a `TYPE_CHECKING` block:

```python
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session, sessionmaker

    from roster_balance.domain.models.principal import Principal
    from roster_balance.domain.models.user import User
```

Keep imports that are used to construct values, execute code, or provide
runtime metadata outside the block. In particular, FastAPI `Annotated` and
Pydantic model annotations may need their types available at runtime. If Ruff
reports `TC001` or `TC003` for such an import, first explain the runtime and
lint tradeoff and ask the user before adding any `# noqa` exception. Prefer a
code change that satisfies both runtime behavior and Ruff; use a narrow inline
`# noqa: TC001` or `# noqa: TC003` only after the user approves it.

Do not move imports merely because they appear in a type annotation. Verify
that postponed annotations make the name unnecessary at runtime, then run the
project quality command:

```text
mise run fmt
```
