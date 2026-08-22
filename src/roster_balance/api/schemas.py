"""HTTP request and response schemas."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


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


class TeamEligibilityCreate(BaseModel):
    member_id: str = Field(min_length=1, max_length=200)


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
