"""Application services for normalized users."""

from datetime import UTC, datetime

from roster_balance.domain.models.principal import Principal
from roster_balance.domain.models.user import User
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
                id=f"{principal.provider}:{principal.subject}",
                provider=principal.provider,
                subject=principal.subject,
                email=None,
                display_name=None,
                active=True,
                created_at=now,
                updated_at=now,
            )
        )
