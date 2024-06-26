from typing import Annotated

from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .. import dependencies
from user_service import bootstrap
from user_service.domains import commands, models
from user_service.entrypoints.schemas import user_schemas
from user_service.service_layer.handlers.command import InvalidOTP
from user_service import views

bus = bootstrap.bootstrap()

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


class UserNotFound(Exception):
    pass


@router.get("/user", status_code=status.HTTP_200_OK)
async def get_user(
    current_user: Annotated[models.User, Depends(dependencies.get_current_unlock_user)]
):
    return current_user


@router.post(
    "/user/{username}/setup-2fa",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=user_schemas.SetupTwoFactorAuthResponse,
)
async def setup_two_factor_auth(cmd: commands.SetupTwoFactorAuthCommand):
    bus.handle(cmd)

    setup_two_factor_auth_response = user_schemas.SetupTwoFactorAuthSchema(
        **cmd.model_dump(), message="OTP code sent"
    )
    return user_schemas.SetupTwoFactorAuthResponse(
        setup_two_factor_auth=setup_two_factor_auth_response
    )


@router.patch(
    "/user/{username}/verify-2fa",
    status_code=status.HTTP_200_OK,
    response_model=user_schemas.VerifyTwoFactorAuthResponse,
)
async def verify_two_factor_auth(cmd: commands.VerifyTwoFactorAuthCommand):
    try:
        bus.handle(cmd)

    except InvalidOTP as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    verify_enable_two_factor_auth_response = user_schemas.VerifyTwoFactorAuthSchema(
        **cmd.model_dump(), message="Two factor authentication enabled"
    )
    return user_schemas.VerifyTwoFactorAuthResponse(
        verify_two_factor_auth=verify_enable_two_factor_auth_response
    )


@router.get(
    "/user/{username}", status_code=status.HTTP_200_OK, response_model=models.Profile
)
async def get_user_profile(username: str):
    try:
        user = views.fetch_models_from_database(
            model_type=models.User, uow=bus.uow, username=username
        )[0]
        if user is None:
            raise UserNotFound("User not found")
        user_profile = views.fetch_models_from_database(
            model_type=models.Profile, uow=bus.uow, user_id=user.id
        )[0]
    except UserNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return user_profile
