from typing import Annotated

import fastapi
import fastapi.security

from .. import dependencies
from user_service import bootstrap
from user_service.domains import commands, models
from user_service.entrypoints.schemas import user_schemas
from user_service.service_layer.handlers.command import InvalidOTP
from user_service import views

bus = bootstrap.bootstrap()

router = fastapi.APIRouter()

oauth2_scheme = fastapi.security.OAuth2PasswordBearer(tokenUrl="login")


class UserNotFound(Exception):
    pass


@router.get("/users/{id}", status_code=fastapi.status.HTTP_200_OK)
async def get_user(
    current_user: Annotated[
        models.User, fastapi.Depends(dependencies.get_current_unlock_user)
    ]
):
    return current_user


@router.post(
    "/users/{id}/setup-2fa",
    status_code=fastapi.status.HTTP_202_ACCEPTED,
)
async def setup_two_factor_auth(id: str, cmd: commands.SetupTwoFactorAuthCommand):
    bus.handle(cmd)

    return fastapi.status.HTTP_202_ACCEPTED


@router.patch(
    "/users/{id}/verify-2fa",
    status_code=fastapi.status.HTTP_200_OK,
)
async def verify_two_factor_auth(id: str, cmd: commands.VerifyTwoFactorAuthCommand):
    try:
        bus.handle(cmd)

    except InvalidOTP as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail=str(e)
        )

    return fastapi.status.HTTP_200_OK


@router.get(
    "/users/{id}/profile",
    status_code=fastapi.status.HTTP_200_OK,
    response_model=models.Profile,
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
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND, detail=str(e)
        )

    return user_profile
