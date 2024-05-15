from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import JSONResponse
from user_service.domains import commands
from ..dependencies import validate_token, UnauthorizedAccess, bus
from user_service.service_layer.handlers import IncorrectCredentials, InvalidOTP

router = APIRouter()


@router.get("/user/{user_id}")
async def get_user(user_id: str, request: Request):
    authorization = request.headers.get("Authorization", "")
    try:
        token = authorization.replace("Bearer ", "")
        validate_token(token, user_id)
    except UnauthorizedAccess as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    cmd = commands.GetUserCommand(user_id, token)
    results = bus.handle(cmd)
    user = results[0]

    return JSONResponse(content={"user": user}, status_code=status.HTTP_200_OK)


@router.post("/user/{user_id}/enable-2fa")
async def enable_two_factor_auth(user_id: str):
    cmd = commands.EnableTwoFactorAuthCommand(user_id)
    results = bus.handle(cmd)
    otp_code = results[0]

    return JSONResponse(
        content={"user_id": user_id, "otp_code": otp_code},
        status_code=status.HTTP_202_ACCEPTED,
    )


@router.patch("/user/{user_id}/verify-enable-2fa")
async def verify_enable_two_factor_auth(user_id: str, request: Request):
    try:
        body = await request.json()
        cmd = commands.VerifyEnableTwoFactorAuthCommand(user_id, **body)
        bus.handle(cmd)

    except (IncorrectCredentials, InvalidOTP) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return JSONResponse(
        content={"message": "Two-Factor Authentication successfully enabled"},
        status_code=status.HTTP_200_OK,
    )
