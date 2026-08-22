"""FastAPI dependency wiring for the application layer."""

import os
from datetime import timedelta

from roster_balance.application.services.member_favorability_service import (
    MemberFavorabilityService,
)
from roster_balance.application.services.rest_rule_service import RestRuleService
from roster_balance.application.services.roster_lane_service import RosterLaneService
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
from roster_balance.infrastructure.db.session import create_session_factory
from roster_balance.infrastructure.email.mailto_invitation_sender import (
    MailtoInvitationSender,
)
from roster_balance.infrastructure.repositories.sqlalchemy_member_favorability_repository import (
    SQLAlchemyMemberFavorabilityRepository,
)
from roster_balance.infrastructure.repositories.sqlalchemy_rest_rule_repository import (
    SQLAlchemyRestRuleRepository,
)
from roster_balance.infrastructure.repositories.sqlalchemy_roster_lane_repository import (
    SQLAlchemyRosterLaneRepository,
)
from roster_balance.infrastructure.repositories.sqlalchemy_team_duty_role_repository import (
    SQLAlchemyTeamDutyRoleRepository,
)
from roster_balance.infrastructure.repositories.sqlalchemy_team_eligibility_repository import (
    SQLAlchemyTeamEligibilityRepository,
)
from roster_balance.infrastructure.repositories.sqlalchemy_team_invitation_repository import (
    SQLAlchemyTeamInvitationRepository,
)
from roster_balance.infrastructure.repositories.sqlalchemy_team_ownership_repository import (
    SQLAlchemyTeamOwnershipRepository,
)
from roster_balance.infrastructure.repositories.sqlalchemy_team_repository import (
    SQLAlchemyTeamRepository,
)
from roster_balance.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)

session_factory = create_session_factory()
user_repository = SQLAlchemyUserRepository(session_factory)
ownership_repository = SQLAlchemyTeamOwnershipRepository(session_factory)
user_service = UserService(user_repository)
team_ownership_service = TeamOwnershipService(ownership_repository)
team_duty_role_service = TeamDutyRoleService(
    SQLAlchemyTeamDutyRoleRepository(session_factory), team_ownership_service
)
team_eligibility_service = TeamEligibilityService(
    SQLAlchemyTeamEligibilityRepository(session_factory),
    team_ownership_service,
    team_duty_role_service,
)
member_favorability_service = MemberFavorabilityService(
    SQLAlchemyMemberFavorabilityRepository(session_factory),
    team_ownership_service,
    team_duty_role_service,
)
rest_rule_service = RestRuleService(
    SQLAlchemyRestRuleRepository(session_factory), team_ownership_service
)
roster_lane_service = RosterLaneService(
    SQLAlchemyRosterLaneRepository(session_factory),
    team_ownership_service,
    rest_rule_service,
)
mailto_invitation_sender = MailtoInvitationSender(
    os.getenv('INVITATION_BASE_URL', 'http://localhost:8000')
)
invitation_sender = mailto_invitation_sender
team_invitation_service = TeamInvitationService(
    SQLAlchemyTeamInvitationRepository(session_factory),
    team_ownership_service,
    user_service,
    invitation_sender,
    expiry=timedelta(
        hours=float(os.getenv('INVITATION_TTL_HOURS', '4')),
    ),
    resend_cooldown=timedelta(
        minutes=float(os.getenv('INVITATION_RESEND_COOLDOWN_MINUTES', '15')),
    ),
)

team_service = TeamService(
    SQLAlchemyTeamRepository(session_factory),
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


def get_member_favorability_service() -> MemberFavorabilityService:
    return member_favorability_service


def get_rest_rule_service() -> RestRuleService:
    return rest_rule_service


def get_roster_lane_service() -> RosterLaneService:
    return roster_lane_service


def get_team_invitation_service() -> TeamInvitationService:
    return team_invitation_service


def get_mailto_invitation_sender() -> MailtoInvitationSender:
    return mailto_invitation_sender
