"""Provider-neutral request identity."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Principal:
    provider: str
    subject: str

    @property
    def user_id(self) -> str:
        return f"{self.provider}:{self.subject}"


DEV_PRINCIPAL = Principal(provider="local", subject="dev")
