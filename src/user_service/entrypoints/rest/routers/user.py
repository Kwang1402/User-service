from typing import Annotated, Dict, Any

import fastapi
import fastapi.security

from .. import dependencies
from user_service import bootstrap
from user_service.domains import commands, models
from user_service.service_layer.handlers.command import InvalidOTP
from user_service.entrypoints.schemas import user_schemas
from user_service import views

bus = bootstrap.bootstrap()

router = fastapi.APIRouter()

oauth2_scheme = fastapi.security.OAuth2PasswordBearer(tokenUrl="login")


class UserNotFound(Exception):
    pass


@router.get("/users/{id}", status_code=fastapi.status.HTTP_200_OK)
async def get_user(
    current_user: Annotated[
        # models.User
        Dict[str, Any],
        fastapi.Depends(dependencies.get_current_unlock_user),
    ]
) -> user_schemas.UserReponse:
    return user_schemas.UserReponse(user=current_user)


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
)
async def get_user_profile(id: str) -> user_schemas.ProfileReponse:
    try:
        user_profile = views.fetch_models_from_database(
            model_type=models.Profile, uow=bus.uow, user_id=id
        )[0]
        if user_profile is None:
            raise UserNotFound("User not found")

    except UserNotFound as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND, detail=str(e)
        )

    return user_schemas.ProfileReponse(profile=user_profile)


@router.get(
    "/users/{id}/friends",
    status_code=fastapi.status.HTTP_200_OK,
)
async def get_user_friends(id: str) -> user_schemas.FriendsResponse:
    users_1 = views.fetch_models_from_database(
        model_type=models.Friend, uow=bus.uow, sender_id=id
    )
    users_2 = views.fetch_models_from_database(
        model_type=models.Friend, uow=bus.uow, receiver_id=id
    )
    friends = [user["receiver_id"] for user in users_1] + [
        user["sender_id"] for user in users_2
    ]

    return user_schemas.FriendsResponse(friends=friends)
