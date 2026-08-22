"""Team rest-rule configuration API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from roster_balance.api.auth import get_principal
from roster_balance.api.dependencies import get_rest_rule_service
from roster_balance.api.schemas import RestRuleCreate, RestRuleResponse
from roster_balance.application.services.rest_rule_service import (
    RestRuleNotFoundError,
    RestRuleService,
)
from roster_balance.application.services.team_ownership_service import (
    OwnershipAuthorizationError,
)
from roster_balance.domain.models.principal import Principal

router = APIRouter(prefix='/teams/{team_id}/rest-rules', tags=['rest-rules'])
RestRules = Annotated[RestRuleService, Depends(get_rest_rule_service)]
PrincipalDependency = Annotated[Principal, Depends(get_principal)]


@router.get('')
def list_rules(
    team_id: str, service: RestRules, principal: PrincipalDependency
) -> list[RestRuleResponse]:
    try:
        return [
            RestRuleResponse.model_validate(rule)
            for rule in service.list_rules(team_id, principal)
        ]
    except OwnershipAuthorizationError as error:
        raise HTTPException(status_code=404, detail='Team not found') from error


@router.get('/{rule_id}')
def get_rule(
    team_id: str,
    rule_id: str,
    service: RestRules,
    principal: PrincipalDependency,
) -> RestRuleResponse:
    try:
        return RestRuleResponse.model_validate(
            service.get_rule(team_id, rule_id, principal)
        )
    except OwnershipAuthorizationError as error:
        raise HTTPException(status_code=404, detail='Team not found') from error
    except RestRuleNotFoundError as error:
        raise HTTPException(status_code=404, detail='Rest rule not found') from error


@router.post('', status_code=status.HTTP_201_CREATED)
def create_rule(
    team_id: str,
    payload: RestRuleCreate,
    service: RestRules,
    principal: PrincipalDependency,
) -> RestRuleResponse:
    try:
        return RestRuleResponse.model_validate(
            service.create_rule(
                team_id, payload.name, payload.cooldown_after, principal
            )
        )
    except OwnershipAuthorizationError as error:
        raise HTTPException(
            status_code=403, detail='Only team owners can configure rest rules'
        ) from error


@router.delete('/{rule_id}', status_code=status.HTTP_204_NO_CONTENT)
def deactivate_rule(
    team_id: str,
    rule_id: str,
    service: RestRules,
    principal: PrincipalDependency,
) -> None:
    try:
        service.deactivate_rule(team_id, rule_id, principal)
    except OwnershipAuthorizationError as error:
        raise HTTPException(
            status_code=403, detail='Only team owners can configure rest rules'
        ) from error
    except RestRuleNotFoundError as error:
        raise HTTPException(status_code=404, detail='Rest rule not found') from error
