"""Owner-managed team availability calendar API routes."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from roster_balance.api.auth import get_principal
from roster_balance.api.dependencies import get_availability_service
from roster_balance.api.schemas import (
    AvailabilityCalendarCreate,
    AvailabilityCalendarPatch,
    AvailabilityCalendarResponse,
    AvailabilityEntryCreate,
    AvailabilityEntryPatch,
    AvailabilityEntryResponse,
)
from roster_balance.application.services.availability_service import (
    AvailabilityCalendarConflictError,
    AvailabilityCalendarNotFoundError,
    AvailabilityEntryNotFoundError,
    AvailabilityService,
)
from roster_balance.application.services.team_ownership_service import (
    OwnershipAuthorizationError,
)
from roster_balance.domain.models.principal import Principal

router = APIRouter(
    prefix='/teams/{team_id}/availability-calendars', tags=['availability-calendars']
)
Service = Annotated[AvailabilityService, Depends(get_availability_service)]
PrincipalDependency = Annotated[Principal, Depends(get_principal)]


@router.get('')
def list_calendars(
    team_id: str, service: Service, principal: PrincipalDependency
) -> list[AvailabilityCalendarResponse]:
    try:
        return [
            AvailabilityCalendarResponse.model_validate(item)
            for item in service.list_calendars(team_id, principal)
        ]
    except OwnershipAuthorizationError as error:
        raise HTTPException(status_code=404, detail='Team not found') from error


@router.post('', status_code=status.HTTP_201_CREATED)
def create_calendar(
    team_id: str,
    payload: AvailabilityCalendarCreate,
    service: Service,
    principal: PrincipalDependency,
) -> AvailabilityCalendarResponse:
    try:
        return AvailabilityCalendarResponse.model_validate(
            service.create_calendar(
                team_id,
                payload.member_id,
                payload.type,
                payload.custom_type,
                payload.name,
                payload.timezone,
                principal,
            )
        )
    except OwnershipAuthorizationError as error:
        raise HTTPException(
            status_code=403, detail='Only team owners can manage calendars'
        ) from error
    except AvailabilityCalendarConflictError as error:
        raise HTTPException(
            status_code=409, detail='Calendar type already exists for member'
        ) from error
    except (AvailabilityCalendarNotFoundError, ValueError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.get('/{calendar_id}')
def get_calendar(
    team_id: str, calendar_id: str, service: Service, principal: PrincipalDependency
) -> AvailabilityCalendarResponse:
    try:
        return AvailabilityCalendarResponse.model_validate(
            service.get_calendar(team_id, calendar_id, principal)
        )
    except (OwnershipAuthorizationError, AvailabilityCalendarNotFoundError) as error:
        raise HTTPException(status_code=404, detail='Calendar not found') from error


@router.patch('/{calendar_id}')
def update_calendar(
    team_id: str,
    calendar_id: str,
    payload: AvailabilityCalendarPatch,
    service: Service,
    principal: PrincipalDependency,
) -> AvailabilityCalendarResponse:
    try:
        return AvailabilityCalendarResponse.model_validate(
            service.update_calendar(
                team_id, calendar_id, payload.name, payload.timezone, principal
            )
        )
    except (OwnershipAuthorizationError, AvailabilityCalendarNotFoundError) as error:
        raise HTTPException(status_code=404, detail='Calendar not found') from error


@router.delete('/{calendar_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_calendar(
    team_id: str, calendar_id: str, service: Service, principal: PrincipalDependency
) -> None:
    try:
        service.delete_calendar(team_id, calendar_id, principal)
    except (OwnershipAuthorizationError, AvailabilityCalendarNotFoundError) as error:
        raise HTTPException(status_code=404, detail='Calendar not found') from error


@router.get('/{calendar_id}/entries')
def list_entries(
    team_id: str, calendar_id: str, service: Service, principal: PrincipalDependency
) -> list[AvailabilityEntryResponse]:
    try:
        return [
            AvailabilityEntryResponse.model_validate(item)
            for item in service.list_entries(team_id, calendar_id, principal)
        ]
    except (OwnershipAuthorizationError, AvailabilityCalendarNotFoundError) as error:
        raise HTTPException(status_code=404, detail='Calendar not found') from error


@router.post('/{calendar_id}/entries', status_code=status.HTTP_201_CREATED)
def add_entry(
    team_id: str,
    calendar_id: str,
    payload: AvailabilityEntryCreate,
    service: Service,
    principal: PrincipalDependency,
) -> AvailabilityEntryResponse:
    try:
        return AvailabilityEntryResponse.model_validate(
            service.add_entry(
                team_id,
                calendar_id,
                payload.starts_at,
                payload.ends_at,
                payload.availability,
                payload.reason,
                principal,
            )
        )
    except (OwnershipAuthorizationError, AvailabilityCalendarNotFoundError) as error:
        raise HTTPException(status_code=404, detail='Calendar not found') from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.post('/{calendar_id}/sources', status_code=status.HTTP_201_CREATED)
async def add_source(
    team_id: str,
    calendar_id: str,
    file: Annotated[UploadFile, File(...)],
    effect: Annotated[str, Form(...)],
    source_format: Annotated[str, Form(...)],
    service: Service,
    principal: PrincipalDependency,
    country: Annotated[str | None, Form()] = None,
    state: Annotated[str | None, Form()] = None,
    county: Annotated[str | None, Form()] = None,
    span_from: Annotated[datetime | None, Form()] = None,
    span_to: Annotated[datetime | None, Form()] = None,
) -> list[AvailabilityEntryResponse]:
    try:
        entries = await file.read()
        return [
            AvailabilityEntryResponse.model_validate(item)
            for item in service.add_icalendar_source(
                team_id,
                calendar_id,
                entries,
                effect,
                source_format,
                file.filename,
                country,
                state,
                county,
                span_from,
                span_to,
                principal,
            )
        ]
    except (OwnershipAuthorizationError, AvailabilityCalendarNotFoundError) as error:
        raise HTTPException(status_code=404, detail='Calendar not found') from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.patch('/{calendar_id}/entries/{entry_id}')
def update_entry(
    team_id: str,
    calendar_id: str,
    entry_id: str,
    payload: AvailabilityEntryPatch,
    service: Service,
    principal: PrincipalDependency,
) -> AvailabilityEntryResponse:
    try:
        return AvailabilityEntryResponse.model_validate(
            service.update_entry(
                team_id,
                calendar_id,
                entry_id,
                payload.starts_at,
                payload.ends_at,
                payload.availability,
                payload.reason,
                principal,
            )
        )
    except (
        OwnershipAuthorizationError,
        AvailabilityCalendarNotFoundError,
        AvailabilityEntryNotFoundError,
    ) as error:
        raise HTTPException(status_code=404, detail='Entry not found') from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.delete(
    '/{calendar_id}/entries/{entry_id}', status_code=status.HTTP_204_NO_CONTENT
)
def delete_entry(
    team_id: str,
    calendar_id: str,
    entry_id: str,
    service: Service,
    principal: PrincipalDependency,
) -> None:
    try:
        service.delete_entry(team_id, calendar_id, entry_id, principal)
    except (
        OwnershipAuthorizationError,
        AvailabilityCalendarNotFoundError,
        AvailabilityEntryNotFoundError,
    ) as error:
        raise HTTPException(status_code=404, detail='Entry not found') from error
