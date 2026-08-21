"""Current-user API route."""

from typing import Annotated

from fastapi import APIRouter, Depends

from roster_balance.api.auth import get_principal
from roster_balance.api.dependencies import get_user_service
from roster_balance.api.schemas import MeResponse, UserResponse
from roster_balance.application.services.user_service import UserService
from roster_balance.domain.models.principal import Principal

router = APIRouter(tags=['identity'])


@router.get('/me')
def get_me(
    principal: Annotated[Principal, Depends(get_principal)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> MeResponse:
    user = service.resolve(principal)
    return MeResponse(
        principal=principal.user_id,
        user=UserResponse.model_validate(user),
    )
