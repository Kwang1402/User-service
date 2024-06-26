from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse

from ..dependencies import create_access_token
from user_service import bootstrap
from user_service.domains import commands, models
from user_service.entrypoints.schemas import login_schemas
from user_service.service_layer.handlers.command import (
    IncorrectCredentials,
    TwoFactorAuthNotEnabled,
)
from user_service import views

bus = bootstrap.bootstrap()

router = APIRouter()


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(cmd: commands.LoginCommand) -> login_schemas.Token:
    try:
        bus.handle(cmd)
        user = views.fetch_models_from_database(
            model_type=models.User, uow=bus.uow, message_id=cmd._id
        )[0]

    except IncorrectCredentials as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    except TwoFactorAuthNotEnabled as e:
        return RedirectResponse(
            url=f"/user/{e.args[0]}/setup-2fa",
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        )
    access_token = create_access_token(data={"sub": user.id})

    return login_schemas.Token(access_token=access_token, toke_type="bearer")
