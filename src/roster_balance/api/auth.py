"""Authentication boundary for local and cloud deployments."""

import os

from fastapi import HTTPException, status

from roster_balance.domain.models.principal import DEV_PRINCIPAL, Principal


def get_principal() -> Principal:
    mode = os.getenv("AUTHENTICATION_MODE", "local")
    if mode == "local":
        return DEV_PRINCIPAL
    if mode == "cognito":
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Cognito authentication is provided by the cloud authorizer",
        )
    raise HTTPException(status_code=500, detail="Unknown authentication mode")
