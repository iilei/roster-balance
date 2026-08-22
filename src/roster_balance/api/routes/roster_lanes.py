"""Roster-lane configuration API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from roster_balance.api.auth import get_principal
from roster_balance.api.dependencies import get_roster_lane_service
from roster_balance.api.schemas import RosterLaneCreate, RosterLaneResponse
from roster_balance.application.services.roster_lane_service import (
    RosterLaneNotFoundError,
    RosterLaneService,
)
from roster_balance.application.services.team_ownership_service import (
    OwnershipAuthorizationError,
)
from roster_balance.domain.models.principal import Principal

router = APIRouter(prefix='/teams/{team_id}/roster-lanes', tags=['roster-lanes'])
RosterLanes = Annotated[RosterLaneService, Depends(get_roster_lane_service)]
PrincipalDependency = Annotated[Principal, Depends(get_principal)]


@router.get('')
def list_lanes(
    team_id: str, service: RosterLanes, principal: PrincipalDependency
) -> list[RosterLaneResponse]:
    try:
        return [
            RosterLaneResponse.model_validate(lane)
            for lane in service.list_lanes(team_id, principal)
        ]
    except OwnershipAuthorizationError as error:
        raise HTTPException(status_code=404, detail='Team not found') from error


@router.get('/{lane_id}')
def get_lane(
    team_id: str,
    lane_id: str,
    service: RosterLanes,
    principal: PrincipalDependency,
) -> RosterLaneResponse:
    try:
        return RosterLaneResponse.model_validate(
            service.get_lane(team_id, lane_id, principal)
        )
    except OwnershipAuthorizationError as error:
        raise HTTPException(status_code=404, detail='Team not found') from error
    except RosterLaneNotFoundError as error:
        raise HTTPException(status_code=404, detail='Roster lane not found') from error


@router.post('', status_code=status.HTTP_201_CREATED)
def create_lane(
    team_id: str,
    payload: RosterLaneCreate,
    service: RosterLanes,
    principal: PrincipalDependency,
) -> RosterLaneResponse:
    try:
        return RosterLaneResponse.model_validate(
            service.create_lane(
                team_id,
                payload.name,
                payload.duration,
                payload.rest_rule_id,
                principal,
            )
        )
    except OwnershipAuthorizationError as error:
        raise HTTPException(
            status_code=403, detail='Only team owners can configure roster lanes'
        ) from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.delete('/{lane_id}', status_code=status.HTTP_204_NO_CONTENT)
def deactivate_lane(
    team_id: str,
    lane_id: str,
    service: RosterLanes,
    principal: PrincipalDependency,
) -> None:
    try:
        service.deactivate_lane(team_id, lane_id, principal)
    except OwnershipAuthorizationError as error:
        raise HTTPException(
            status_code=403, detail='Only team owners can configure roster lanes'
        ) from error
    except RosterLaneNotFoundError as error:
        raise HTTPException(status_code=404, detail='Roster lane not found') from error
