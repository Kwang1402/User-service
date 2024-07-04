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
async def login(form_data: Annotated[fastapi.security.OAuth2PasswordRequestForm, fastapi.Depends()]) -> login_schemas.Token:
    try:
        cmd = commands.LoginCommand(username=form_data.username, password=form_data.password)
        bus.handle(cmd)
        user = views.fetch_models_from_database(
            model_type=models.User, uow=bus.uow, message_id=cmd._id
        )[0]

    except command.IncorrectCredentials as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    except command.TwoFactorAuthNotEnabled as e:
        return fastapi.responses.RedirectResponse(
            url=f"/users/{e.args[0]}/setup-2fa",
        )
    access_token = dependencies.create_access_token(data={"sub": user.id})

    return login_schemas.Token(access_token=access_token, toke_type="bearer")
