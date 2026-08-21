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
    role: Literal["owner"] = "owner"
    created_at: datetime


class TeamEligibilityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    team_id: str
    member_id: str
    created_at: datetime
