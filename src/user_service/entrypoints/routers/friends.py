from typing import Annotated

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from user_service.domains import commands
from ..dependencies import bus
from user_service.entrypoints import schemas
from user_service.config import SECRET_KEY
from user_service import views

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.post("/add-friend", status_code=status.HTTP_201_CREATED)
async def add_friend(
    body: schemas.AddFriendSchema, token: Annotated[str, Depends(oauth2_scheme)]
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        token_user_id: str = payload.get("sub")
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    cmd = commands.AddFriendCommand(sender_id=token_user_id, **body.model_dump())
    bus.handle(cmd)

    return JSONResponse(content={"message": "Friend request sent"}, status_code=status.HTTP_201_CREATED)


@router.get("/friend-requests", status_code=status.HTTP_200_OK)
async def get_friend_requests(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        token_user_id: str = payload.get("sub")
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    friend_requests = views.fetch_models_from_database(
        "friend_requests",
        f"receiver_id = '{token_user_id}' AND status = 'Pending'",
        bus.uow,
    )

    for friend_request in friend_requests:
        friend_request['created_time'] = str(friend_request['created_time'])
        friend_request['updated_time'] = str(friend_request['updated_time'])

    return JSONResponse(content=friend_requests, status_code=status.HTTP_200_OK)


@router.patch("/accept-friend-request", status_code=status.HTTP_200_OK)
async def accept_friend_request(
    body: schemas.AcceptFriendRequestSchema,
    token: Annotated[str, Depends(oauth2_scheme)],
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        token_user_id: str = payload.get("sub")

        friend_request = views.fetch_models_from_database(
            "friend_request", f"id = '{body.friend_request_id}'", bus.uow
        )[0]
        if token_user_id != friend_request["receiver_id"]:
            raise InvalidTokenError("Not authenticated")

    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    cmd = commands.AcceptFriendRequestCommand(**body.model_dump())
    bus.handle(cmd)

    return JSONResponse(
        content={"message": "Accepted friend request"}, status_code=status.HTTP_200_OK
    )


@router.patch("decline-friend-request", status_code=status.HTTP_200_OK)
async def decline_friend_request(
    body: schemas.DeclineFriendRequestSchema,
    token: Annotated[str, Depends(oauth2_scheme)],
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        token_user_id: str = payload.get("sub")

        friend_request = views.fetch_models_from_database(
            "friend_request", f"id = '{body.friend_request_id}'", bus.uow
        )[0]
        if token_user_id != friend_request["receiver_id"]:
            raise InvalidTokenError("Not authenticated")

    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    cmd = commands.DeclineFriendRequestCommand(**body.model_dump())
    bus.handle(cmd)

    return JSONResponse(
        content={"message": "Declined friend request"}, status_code=status.HTTP_200_OK
    )
