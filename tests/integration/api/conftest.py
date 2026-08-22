from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from sqlalchemy import delete

from roster_balance.api import dependencies
from roster_balance.infrastructure.db.models import (
    TeamDutyRoleModel,
    TeamEligibilityModel,
    TeamInvitationModel,
    TeamMembershipModel,
    TeamModel,
)

if TYPE_CHECKING:
    from collections.abc import Generator


def _clear_teams() -> None:
    with dependencies.session_factory.begin() as session:
        for model in (
            TeamInvitationModel,
            TeamEligibilityModel,
            TeamDutyRoleModel,
            TeamMembershipModel,
            TeamModel,
        ):
            session.execute(delete(model))


@pytest.fixture(autouse=True)
def clear_teams() -> Generator[None]:
    _clear_teams()
    yield
    _clear_teams()
