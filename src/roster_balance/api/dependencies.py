"""FastAPI dependency wiring for the application layer."""

import os
from datetime import timedelta

from roster_balance.application.services.team_duty_role_service import (
    TeamDutyRoleService,
)
from roster_balance.application.services.team_eligibility_service import (
    TeamEligibilityService,
)
from roster_balance.application.services.team_invitation_service import (
    TeamInvitationService,
)
from roster_balance.application.services.team_ownership_service import (
    TeamOwnershipService,
)
from roster_balance.application.services.team_service import TeamService
from roster_balance.application.services.user_service import UserService
from roster_balance.domain.team_ids import TeamIdSpace
from roster_balance.infrastructure.email.in_memory_invitation_sender import (
    InMemoryInvitationSender,
)
from roster_balance.infrastructure.repositories.in_memory_team_duty_role_repository import (
    InMemoryTeamDutyRoleRepository,
)
from roster_balance.infrastructure.repositories.in_memory_team_eligibility_repository import (
    InMemoryTeamEligibilityRepository,
)
from roster_balance.infrastructure.repositories.in_memory_team_invitation_repository import (
    InMemoryTeamInvitationRepository,
)
from roster_balance.infrastructure.repositories.in_memory_team_ownership_repository import (
    InMemoryTeamOwnershipRepository,
)
from roster_balance.infrastructure.repositories.in_memory_team_repository import (
    InMemoryTeamRepository,
)
from roster_balance.infrastructure.repositories.in_memory_user_repository import (
    InMemoryUserRepository,
)

user_repository = InMemoryUserRepository()
ownership_repository = InMemoryTeamOwnershipRepository()
user_service = UserService(user_repository)
team_ownership_service = TeamOwnershipService(ownership_repository)
team_duty_role_service = TeamDutyRoleService(
    InMemoryTeamDutyRoleRepository(), team_ownership_service
)
team_eligibility_service = TeamEligibilityService(
    InMemoryTeamEligibilityRepository(),
    team_ownership_service,
    team_duty_role_service,
)
invitation_sender = InMemoryInvitationSender()
team_invitation_service = TeamInvitationService(
    InMemoryTeamInvitationRepository(),
    team_ownership_service,
    user_service,
    invitation_sender,
    expiry=timedelta(
        hours=float(os.getenv('INVITATION_COOLDOWN_HOURS', '4')),
    ),
)

team_service = TeamService(
    InMemoryTeamRepository(),
    TeamIdSpace(
        maximum_teams=int(os.getenv('TEAM_MAXIMUM', '1000000')),
        seed=os.getenv('TEAM_ID_SEED', 'local-development'),
    ),
    user_service=user_service,
    ownership_service=team_ownership_service,
)


def get_team_service() -> TeamService:
    return team_service


def get_user_service() -> UserService:
    return user_service


def get_team_ownership_service() -> TeamOwnershipService:
    return team_ownership_service


def get_team_eligibility_service() -> TeamEligibilityService:
    return team_eligibility_service


def get_team_duty_role_service() -> TeamDutyRoleService:
    return team_duty_role_service


def get_team_invitation_service() -> TeamInvitationService:
    return team_invitation_service
