import logging
from typing import List, Dict, Callable, Type
from user_service.domains import commands, events, models
from user_service.service_layer import unit_of_work
from user_service.config import secret_key
import jwt
from flask_bcrypt import Bcrypt
import string

bcrypt = Bcrypt()


class InvalidPassword(Exception):
    pass


class EmailExisted(Exception):
    pass


class IncorrectCredentials(Exception):
    pass


class UnathorizedAccess(Exception):
    pass


def validate_password(password: str) -> bool:
    # Minimum length
    if len(password) < 8:
        return False

    # No spaces
    if " " in password:
        return False

    # At least one digit
    if not any(c.isdigit() for c in password):
        return False

    # At least one special character
    if not any(c in string.punctuation for c in password):
        return False

    return True


def register(
    cmd: commands.RegisterCommand,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        if validate_password(cmd.password) is False:
            raise InvalidPassword(f"Invalid password '{cmd.password}'")
        user = uow.users.get_by_email(email=cmd.email)
        if user:
            raise EmailExisted(f"Email {cmd.email} already existed")

        hashed_password = bcrypt.generate_password_hash(cmd.password).decode("utf-8")

        user = models.User(cmd.username, cmd.email, hashed_password)
        uow.users.add(user)
        user.events.append(
            events.Registered(user.id, cmd.backup_email, cmd.gender, cmd.date_of_birth)
        )

        uow.commit()


def create_user_profile(
    event: events.Registered,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        profile = models.Profile(
            event.user_id, event.backup_email, event.gender, event.date_of_birth
        )
        user = uow.users.get(id=event.user_id)
        user.profile = profile

        uow.commit()


def login(
    cmd: commands.LoginCommand,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        user = uow.users.get_by_email(email=cmd.email)
        if user is None or not bcrypt.check_password_hash(user.password, cmd.password):
            raise IncorrectCredentials("Incorrect email or password")

        token = jwt.encode({"user_id": user.id}, secret_key, algorithm="HS256")

        return token


def get_user(
    cmd: commands.GetUserCommand,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        if not cmd.token:
            raise UnathorizedAccess("Authorization token missing")

        try:
            decoded_token = jwt.decode(cmd.token, secret_key, algorithms=["HS256"])
            authenticated_user_id = decoded_token.get("user_id")

            if authenticated_user_id != cmd.user_id:
                raise UnathorizedAccess("Unauthorized access to user account")

            user = uow.users.get(cmd.user_id)
            return {"username": user.username, "email": user.email}
        except jwt.InvalidTokenError:
            raise UnathorizedAccess("Invalid token")


EVENT_HANDLERS = {
    events.Registered: [create_user_profile],
}

COMMAND_HANDLERS = {
    commands.RegisterCommand: register,
    commands.LoginCommand: login,
    commands.GetUserCommand: get_user,
}
