"""Team API routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from roster_balance.api.schemas import TeamCreate, TeamPatch, TeamResponse
from roster_balance.application.services.team_service import (
	TeamNameConflictError,
	TeamNotFoundError,
	TeamService,
)

router = APIRouter(prefix="/teams", tags=["teams"])


def get_team_service() -> TeamService:
	from roster_balance.main import team_service

	return team_service


Service = Annotated[TeamService, Depends(get_team_service)]


@router.get("", response_model=list[TeamResponse])
def list_teams(service: Service) -> list[TeamResponse]:
	return service.list_teams()


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(payload: TeamCreate, service: Service) -> TeamResponse:
	try:
		return service.create_team(payload.name, payload.description)
	except TeamNameConflictError as error:
		raise HTTPException(status_code=409, detail="A team with this name already exists") from error


@router.get("/{team_id}", response_model=TeamResponse)
def get_team(team_id: UUID, service: Service) -> TeamResponse:
	try:
		return service.get_team(team_id)
	except TeamNotFoundError as error:
		raise HTTPException(status_code=404, detail="Team not found") from error


@router.patch("/{team_id}", response_model=TeamResponse)
def update_team(team_id: UUID, payload: TeamPatch, service: Service) -> TeamResponse:
	try:
		return service.update_team(team_id, **payload.model_dump(exclude_unset=True))
	except TeamNotFoundError as error:
		raise HTTPException(status_code=404, detail="Team not found") from error
	except TeamNameConflictError as error:
		raise HTTPException(status_code=409, detail="A team with this name already exists") from error


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(team_id: UUID, service: Service) -> Response:
	try:
		service.delete_team(team_id)
	except TeamNotFoundError as error:
		raise HTTPException(status_code=404, detail="Team not found") from error
	return Response(status_code=status.HTTP_204_NO_CONTENT)
