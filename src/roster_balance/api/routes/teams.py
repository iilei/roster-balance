"""Team API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from roster_balance.api.auth import get_principal
from roster_balance.api.dependencies import get_team_service
from roster_balance.api.schemas import TeamCreate, TeamPatch, TeamResponse
from roster_balance.application.services.team_service import (
    TeamNameConflictError,
    TeamNotFoundError,
    TeamService,
)
from roster_balance.domain.models.principal import Principal

router = APIRouter(prefix='/teams', tags=['teams'])


Service = Annotated[TeamService, Depends(get_team_service)]


@router.get('')
def list_teams(
    _principal: Annotated[Principal, Depends(get_principal)],
    service: Service,
    q: Annotated[str | None, Query(min_length=1, max_length=200)] = None,
) -> list[TeamResponse]:
    teams = service.list_teams() if q is None else service.search_teams(q)
    return [TeamResponse.model_validate(team) for team in teams]


@router.post('', status_code=status.HTTP_201_CREATED)
def create_team(
    payload: TeamCreate,
    service: Service,
    principal: Annotated[Principal, Depends(get_principal)],
) -> TeamResponse:
    try:
        return TeamResponse.model_validate(
            service.create_team(payload.name, payload.description, principal),
        )
    except TeamNameConflictError as error:
        raise HTTPException(
            status_code=409,
            detail='A team with this name already exists',
        ) from error


@router.get('/{team_id}')
def get_team(
    team_id: str,
    service: Service,
    principal: Annotated[Principal, Depends(get_principal)],
) -> TeamResponse:
    try:
        return TeamResponse.model_validate(
            service.get_team_for_member(team_id, principal.user_id),
        )
    except TeamNotFoundError as error:
        raise HTTPException(status_code=404, detail='Team not found') from error


@router.patch('/{team_id}')
def update_team(
    team_id: str,
    payload: TeamPatch,
    service: Service,
    principal: Annotated[Principal, Depends(get_principal)],
) -> TeamResponse:
    try:
        return TeamResponse.model_validate(
            service.update_team_for_owner(
                team_id,
                principal.user_id,
                **payload.model_dump(exclude_unset=True),
            ),
        )
    except TeamNotFoundError as error:
        raise HTTPException(status_code=404, detail='Team not found') from error
    except TeamNameConflictError as error:
        raise HTTPException(
            status_code=409,
            detail='A team with this name already exists',
        ) from error
    except PermissionError as error:
        raise HTTPException(
            status_code=403,
            detail='Team owner access required',
        ) from error


@router.delete('/{team_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_team(
    team_id: str,
    service: Service,
    principal: Annotated[Principal, Depends(get_principal)],
) -> Response:
    try:
        service.delete_team_for_owner(team_id, principal.user_id)
    except TeamNotFoundError as error:
        raise HTTPException(status_code=404, detail='Team not found') from error
    except PermissionError as error:
        raise HTTPException(
            status_code=403, detail='Team owner access required'
        ) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
