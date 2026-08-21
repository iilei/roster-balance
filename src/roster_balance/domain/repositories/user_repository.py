"""Repository boundary for normalized users."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    import builtins

    from roster_balance.domain.models.principal import Principal
    from roster_balance.domain.models.user import User


class UserRepository(Protocol):
    def list(self) -> builtins.list[User]: ...

    def get(self, user_id: str) -> User | None: ...

    def get_by_principal(self, principal: Principal) -> User | None: ...

    def add(self, user: User) -> User: ...
