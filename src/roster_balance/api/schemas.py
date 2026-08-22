"""HTTP request and response schemas."""

import os
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from roster_balance.domain.durations import parse_duration


def _max_factoring_entity_duration_seconds() -> int:
    return int(os.getenv('MAX_FACTORING_ENTITY_DURATION_SECONDS', '604800'))


class TeamCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)


class TeamPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    active: bool | None = None


class TeamResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None
    active: bool
    created_at: datetime
    updated_at: datetime


class TeamMembershipResponse(BaseModel):
    team: TeamResponse
    role: Literal['owner', 'member']


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    provider: str
    subject: str
    email: str | None
    display_name: str | None
    active: bool
    created_at: datetime
    updated_at: datetime


class MeResponse(BaseModel):
    principal: str
    user: UserResponse


class TeamOwnerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    team_id: str
    user_id: str
    role: Literal['owner', 'member']
    created_at: datetime


class TeamEligibilityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    team_id: str
    member_id: str
    duty_role_id: str
    duty_role: str
    created_at: datetime


class TeamDutyRoleCreate(BaseModel):
    slug: str = Field(min_length=1, max_length=80)
    display_name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)


class TeamDutyRoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    team_id: str
    slug: str
    display_name: str
    description: str | None
    active: bool
    created_at: datetime
    updated_at: datetime


class RestRuleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    cooldown_after: int

    @field_validator('cooldown_after', mode='before')
    @classmethod
    def parse_cooldown_after(cls, value: object) -> int:
        max_seconds = _max_factoring_entity_duration_seconds()
        if isinstance(value, int):
            if value <= 0:
                raise ValueError('cooldown_after must be greater than zero')
            seconds = value
        else:
            seconds = parse_duration(value, max_seconds=max_seconds)
        if seconds > max_seconds:
            raise ValueError('cooldown_after exceeds the configured maximum')
        return seconds


class RestRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    team_id: str
    name: str
    cooldown_after: int
    active: bool
    created_at: datetime
    updated_at: datetime


class RosterLaneCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    duration: int
    rest_rule_id: str = Field(min_length=1, max_length=36)

    @field_validator('duration', mode='before')
    @classmethod
    def parse_duration_value(cls, value: object) -> int:
        max_seconds = _max_factoring_entity_duration_seconds()
        if isinstance(value, int):
            seconds = value
        else:
            seconds = parse_duration(value, max_seconds=max_seconds)
        if seconds <= 0:
            raise ValueError('duration must be greater than zero')
        if seconds > max_seconds:
            raise ValueError('duration exceeds the configured maximum')
        return seconds


class RosterLaneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    team_id: str
    name: str
    duration: int
    rest_rule_id: str
    active: bool
    created_at: datetime
    updated_at: datetime


class TeamEligibilityCreate(BaseModel):
    member_id: str = Field(min_length=1, max_length=200)


class MemberFavorabilityCreate(BaseModel):
    effect: str = Field(min_length=1, max_length=32)
    blocking_level: str | None = Field(default=None, min_length=1, max_length=16)
    favorability: float | None = None
    constraint_strength: float | None = None


class MemberFavorabilityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    team_id: str
    member_id: str
    duty_role_id: str
    effect: str
    blocking_level: str | None
    favorability: float | None
    constraint_strength: float | None
    source: str
    created_at: datetime
    updated_at: datetime


class TeamInvitationCreate(BaseModel):
    email: str = Field(min_length=3, max_length=320)


class TeamInvitationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: str
    expires_at: datetime


class TeamInvitationSubmissionResponse(BaseModel):
    status: str


class TeamInvitationPreviewResponse(BaseModel):
    team_id: str
    role: str
    expires_at: datetime


class TeamInvitationAccept(BaseModel):
    token: str = Field(min_length=1, max_length=512)


class LocalInvitationDeliveryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    invitation_id: str
    mailto_url: str
    preview_url: str
    accept_url: str
