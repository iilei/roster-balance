"""Application services for normalized users."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from roster_balance.domain.models.user import User

if TYPE_CHECKING:
    from roster_balance.domain.models.principal import Principal
    from roster_balance.domain.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def resolve(self, principal: Principal) -> User:
        user = self._repository.get_by_principal(principal)
        if user is not None:
            return user
        now = datetime.now(UTC)
        return self._repository.add(
            User(
                id=f'{principal.provider}:{principal.subject}',
                provider=principal.provider,
                subject=principal.subject,
                email=(
                    principal.verified_email.strip().casefold()
                    if principal.verified_email is not None
                    else None
                ),
                display_name=None,
                active=True,
                created_at=now,
                updated_at=now,
            ),
        )
