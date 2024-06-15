from typing import Annotated

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from user_service.domains import commands
from ..dependencies import bus
from user_service.entrypoints import schemas
from user_service.service_layer.handlers import IncorrectCredentials, InvalidOTP
from user_service.config import SECRET_KEY
from user_service import views

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.get(
    "/user/{user_id}",
    tags=["users"],
    summary="Get the user account",
    responses={
        status.HTTP_200_OK: {
            "content": {
                "application/json": {
                    "example": {"user": {"username": "string", "email": "string"}}
                }
            }
        },
        status.HTTP_401_UNAUTHORIZED: {
            "content": {"application/json": {"example": {"detail": "string"}}}
        },
    },
)
async def get_user(user_id: str, token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        token_user_id: str = payload.get("sub")
        if token_user_id != user_id:
            raise InvalidTokenError("Not authenticated")
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = views.fetch_model_from_database(user_id, "users", bus.uow)
    print(user)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return JSONResponse(
        content={"user": {"username": user["username"], "email": user["email"]}},
        status_code=status.HTTP_200_OK,
    )


@router.post(
    "/user/{user_id}/enable-2fa",
    tags=["users"],
    summary="Send OTP code to enable 2FA",
    responses={
        status.HTTP_202_ACCEPTED: {
            "content": {"application/json": {"example": {"user_id": "string"}}}
        },
    },
)
async def enable_two_factor_auth(user_id: str):
    cmd = commands.EnableTwoFactorAuthCommand(user_id=user_id)
    bus.handle(cmd)

    return JSONResponse(
        content={"user_id": user_id},
        status_code=status.HTTP_202_ACCEPTED,
    )


@router.patch(
    "/user/{user_id}/verify-enable-2fa",
    tags=["users"],
    summary="Verify OTP code to enable 2FA",
    responses={
        status.HTTP_200_OK: {
            "content": {
                "application/json": {
                    "example": {
                        "message": "Two-Factor Authentication successfully enabled"
                    }
                }
            }
        },
        status.HTTP_400_BAD_REQUEST: {
            "content": {"application/json": {"example": {"detail": "string"}}}
        },
    },
)
async def verify_enable_two_factor_auth(
    user_id: str, body: schemas.VerifyEnableTwoFactorAuthSchema
):
    try:
        cmd = commands.VerifyEnableTwoFactorAuthCommand(
            user_id=user_id, **body.model_dump()
        )
        bus.handle(cmd)

    except (IncorrectCredentials, InvalidOTP) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return JSONResponse(
        content={"message": "Two-Factor Authentication successfully enabled"},
        status_code=status.HTTP_200_OK,
    )
