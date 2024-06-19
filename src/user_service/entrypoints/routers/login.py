from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import JSONResponse, RedirectResponse
from user_service.domains import commands
from ..dependencies import bus
from user_service.service_layer.handlers import (
    IncorrectCredentials,
    TwoFactorAuthNotEnabled,
)

router = APIRouter()


@router.post("/login")
async def login(request: Request):
    try:
        body = await request.json()
        cmd = commands.LoginCommand(**body)
        results = bus.handle(cmd)
        user_id, token = results[0]

    except IncorrectCredentials as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    except TwoFactorAuthNotEnabled as e:
        return RedirectResponse(
            url=f"/user/{e.args[0]}/enable-2fa",
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        )

    return JSONResponse(
        content={"user_id": user_id, "token": token}, status_code=status.HTTP_200_OK
    )
