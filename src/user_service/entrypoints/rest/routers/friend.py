from typing import Annotated, List, Dict, Any

import fastapi

from .. import dependencies
from user_service import bootstrap
from user_service.domains import commands, models
from user_service.entrypoints.schemas import (
    friend_schemas,
)
from user_service import views

bus = bootstrap.bootstrap()

router = fastapi.APIRouter()


# API conventions: https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design
@router.post(
    "/friend-requests",
    status_code=fastapi.status.HTTP_201_CREATED,
)
async def send_friend_request(
    cmd: commands.FriendRequestCommand,
) -> friend_schemas.FriendRequestResponse:
    bus.handle(cmd)

    friend_request = views.fetch_models_from_database(
        model_type=models.FriendRequest, uow=bus.uow, message_id=cmd._id
    )[0]

    return friend_schemas.FriendRequestResponse(friend_request=friend_request)


@router.get(
    "/friend-requests",
    status_code=fastapi.status.HTTP_200_OK,
)
async def get_friend_requests(
    current_user: Annotated[
        Dict[str, Any], fastapi.Depends(dependencies.get_current_unlock_user)
    ]
) -> friend_schemas.FriendRequestsResponse:
    friend_requests = views.fetch_models_from_database(
        model_type=models.FriendRequest,
        uow=bus.uow,
        receiver_id=current_user["id"],
    )

    return friend_schemas.FriendRequestsResponse(friend_requests=friend_requests)


@router.post(
    "/friend-requests/{id}/accept",
    status_code=fastapi.status.HTTP_200_OK,
)
async def accept_friend_request(
    cmd: commands.AcceptFriendRequestCommand,
) -> friend_schemas.AcceptFriendRequestResponse:
    bus.handle(cmd)

    friend_request = views.fetch_models_from_database(
        model_type=models.FriendRequest, uow=bus.uow, id=cmd.friend_request.id
    )[0]

    return friend_schemas.AcceptFriendRequestResponse(friend_request=friend_request)


@router.delete(
    "/friend-requests/{id}/decline",
    status_code=fastapi.status.HTTP_204_NO_CONTENT,
)
async def decline_friend_request(cmd: commands.DeclineFriendRequestCommand):
    bus.handle(cmd)

    return fastapi.status.HTTP_204_NO_CONTENT
