"""Local invitation delivery as a mailto link."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from urllib.parse import quote, urlencode

if TYPE_CHECKING:
    from roster_balance.domain.models.team_invitation import TeamInvitation


@dataclass(frozen=True, slots=True)
class LocalInvitationDelivery:
    invitation_id: str
    mailto_url: str
    preview_url: str
    accept_url: str


class MailtoInvitationSender:
    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip('/')
        self._deliveries: dict[str, LocalInvitationDelivery] = {}

    def send(self, invitation: TeamInvitation, token: str) -> None:
        preview_url = self._invitation_url(invitation.id, 'preview', token)
        accept_url = self._invitation_url(invitation.id, 'accept', token)
        body = (
            f'You are invited to join team {invitation.team_id} as a team member.\n\n'
            f'Review the invitation: {preview_url}\n'
            f'Accept the invitation: {accept_url}\n'
            f'This invitation expires at {invitation.expires_at.isoformat()}.'
        )
        mailto_url = (
            'mailto:'
            + invitation.email
            + '?'
            + urlencode(
                {'subject': 'Team invitation', 'body': body},
                quote_via=quote,
            )
        )
        self._deliveries[invitation.id] = LocalInvitationDelivery(
            invitation.id,
            mailto_url,
            preview_url,
            accept_url,
        )

    def get(self, invitation_id: str) -> LocalInvitationDelivery | None:
        return self._deliveries.get(invitation_id)

    def latest(self) -> LocalInvitationDelivery | None:
        return next(reversed(self._deliveries.values()), None)

    def _invitation_url(self, invitation_id: str, action: str, token: str) -> str:
        path = f'{self._base_url}/invitations/{invitation_id}/{action}'
        return f'{path}?{urlencode({"token": token})}'
