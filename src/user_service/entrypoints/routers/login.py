from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from user_service.domains import commands
from ..dependencies import bus, create_access_token
from ..schemas import Token
from user_service.service_layer.handlers import (
    IncorrectCredentials,
    TwoFactorAuthNotEnabled,
)

router = APIRouter()


@router.post(
    "/login",
    tags=["users"],
    summary="Login for user",
    responses={
        status.HTTP_200_OK: {
            "content": {
                "application/json": {
                    "example": {
                        "user_id": "string",
                        "token": {"access_token": "string", "token_type": "str"},
                    }
                }
            }
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
            "content": {"application/json": {"example": {"detail": "string"}}},
        },
    },
)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    try:
        cmd = commands.LoginCommand(form_data.username, form_data.password)
        results = bus.handle(cmd)
        user_id = results[0]

    except IncorrectCredentials as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    except TwoFactorAuthNotEnabled as e:
        return RedirectResponse(
            url=f"/user/{e.args[0]}/enable-2fa",
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        )
    access_token = create_access_token(data={"sub": user_id})

    return JSONResponse(
        content={
            "user_id": user_id,
            "token": Token(access_token=access_token, token_type="bearer").model_dump(),
        },
        status_code=status.HTTP_200_OK,
    )
