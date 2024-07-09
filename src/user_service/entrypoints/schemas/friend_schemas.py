from typing import List
from datetime import datetime

import pydantic


class FriendRequestBase(pydantic.BaseModel):
    sender_id: str
    receiver_id: str


class FriendRequestSchema(FriendRequestBase):
    model_config = pydantic.ConfigDict(from_attributes=True, extra="allow")

    id: str
    created_time: datetime = pydantic.Field(default_factory=datetime.now)
    updated_time: datetime = pydantic.Field(default_factory=datetime.now)


class FriendRequestResponse(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    friend_request: FriendRequestSchema


class FriendRequestsResponse(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    friend_requests: List[FriendRequestSchema]


class AcceptFriendRequestBase(pydantic.BaseModel):
    friend_request: FriendRequestSchema


class AcceptFriendRequestSchema(AcceptFriendRequestBase):
    model_config = pydantic.ConfigDict(from_attributes=True, extra="allow")


class AcceptFriendRequestResponse(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    friend_request: AcceptFriendRequestSchema


class DeclineFriendRequestBase(pydantic.BaseModel):
    friend_request: FriendRequestSchema
