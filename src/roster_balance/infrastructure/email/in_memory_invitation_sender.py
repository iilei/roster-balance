"""No-op invitation sender for local development and tests."""


class InMemoryInvitationSender:
    def __init__(self) -> None:
        self.sent: list[tuple[str, str]] = []

    def send(self, invitation, token: str) -> None:
        self.sent.append((invitation.email, token))
