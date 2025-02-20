from typing import Annotated

import fastapi
import fastapi.security
import fastapi.responses

from .. import dependencies
from user_service import bootstrap
from user_service.domains import commands, models
from user_service.entrypoints.schemas import login_schemas
from user_service.service_layer.handlers import command
from user_service import views

bus = bootstrap.bootstrap()

router = fastapi.APIRouter()


@router.post("/login", status_code=fastapi.status.HTTP_200_OK)
async def login(
    form_data: Annotated[fastapi.security.OAuth2PasswordRequestForm, fastapi.Depends()]
) -> login_schemas.LoginResponse:
    try:
        cmd = commands.LoginCommand(
            username=form_data.username, password=form_data.password
        )
        bus.handle(cmd)
        users = views.fetch_models_from_database(
            model_type=models.User, uow=bus.uow, username=form_data.username
        )
        if not users:
            users = views.fetch_models_from_database(
                model_type=models.User, uow=bus.uow, email=form_data.username
            )
        user = users[0]

    except command.IncorrectCredentials as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    except command.TwoFactorAuthNotEnabled as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Two-factor authentication required. Please set up 2FA",
                # "url" : f"users/{e.args[0]}/setup-2fa"
                "user_id": e.args[0],
            },
        )

    access_token = dependencies.create_access_token(data={"sub": user["id"]})
    token = login_schemas.Token(access_token=access_token, token_type="bearer")

    return login_schemas.LoginResponse(token=token)
