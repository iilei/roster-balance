"""Member favorability and blocking configuration routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from roster_balance.api.auth import get_principal
from roster_balance.api.dependencies import get_member_favorability_service
from roster_balance.api.schemas import (
    MemberFavorabilityCreate,
    MemberFavorabilityResponse,
)
from roster_balance.application.services.member_favorability_service import (
    MemberFavorabilityConflictError,
    MemberFavorabilityNotFoundError,
    MemberFavorabilityService,
)
from roster_balance.application.services.team_ownership_service import (
    OwnershipAuthorizationError,
)
from roster_balance.domain.models.principal import Principal

router = APIRouter(
    prefix='/teams/{team_id}/members/{member_id}/favorability',
    tags=['member-favorability'],
)
MemberFavorabilityDependency = Annotated[
    MemberFavorabilityService, Depends(get_member_favorability_service)
]
PrincipalDependency = Annotated[Principal, Depends(get_principal)]


@router.get('')
def list_member_favorability(
    team_id: str,
    member_id: str,
    service: MemberFavorabilityDependency,
    principal: PrincipalDependency,
) -> list[MemberFavorabilityResponse]:
    try:
        return [
            MemberFavorabilityResponse.model_validate(item)
            for item in service.list_for_member(team_id, member_id, principal)
        ]
    except OwnershipAuthorizationError as error:
        raise HTTPException(
            status_code=403, detail='Only team owners can view favorability'
        ) from error


@router.post('/{duty_role_id}', status_code=201)
def create_member_favorability(
    team_id: str,
    member_id: str,
    duty_role_id: str,
    payload: MemberFavorabilityCreate,
    service: MemberFavorabilityDependency,
    principal: PrincipalDependency,
) -> MemberFavorabilityResponse:
    try:
        return MemberFavorabilityResponse.model_validate(
            service.create_favorability(
                team_id=team_id,
                member_id=member_id,
                duty_role_id=duty_role_id,
                effect=payload.effect,
                blocking_level=payload.blocking_level,
                favorability=payload.favorability,
                constraint_strength=payload.constraint_strength,
                principal=principal,
            )
        )
    except OwnershipAuthorizationError as error:
        raise HTTPException(
            status_code=403, detail='Only team owners can update favorability'
        ) from error
    except MemberFavorabilityConflictError as error:
        raise HTTPException(
            status_code=409, detail='Favorability already exists'
        ) from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.delete('/{duty_role_id}', status_code=204)
def delete_member_favorability(
    team_id: str,
    member_id: str,
    duty_role_id: str,
    service: MemberFavorabilityDependency,
    principal: PrincipalDependency,
) -> None:
    try:
        service.delete_favorability(team_id, member_id, duty_role_id, principal)
    except OwnershipAuthorizationError as error:
        raise HTTPException(
            status_code=403, detail='Only team owners can update favorability'
        ) from error
    except MemberFavorabilityNotFoundError as error:
        raise HTTPException(status_code=404, detail='Favorability not found') from error
