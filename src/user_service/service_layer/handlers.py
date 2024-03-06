import logging
from typing import List, Dict, Callable, Type
from user_service.domains import commands, events, models
from user_service.service_layer import unit_of_work

import uuid
import string


class InvalidPassword(Exception):
    pass


class EmailExisted(Exception):
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

        user = models.User(cmd.username, cmd.email, cmd.password)
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


EVENT_HANDLERS = {
    events.Registered: [create_user_profile],
}

COMMAND_HANDLERS = {
    commands.RegisterCommand: register,
}
