from typing import List, Dict, Callable, Type
from user_service.domains import commands, events, models
from user_service.service_layer import unit_of_work


class EmailExisted(Exception):
    pass


class IncorrectCredentials(Exception):
    pass


def register(
    cmd: commands.RegisterCommand,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        user = uow.repo.get(models.User, email=cmd.email)
        if user:
            raise EmailExisted(f"Email {cmd.email} already existed")

        user = models.User(cmd.username, cmd.email, cmd.password)
        uow.repo.add(user)
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
        uow.repo.add(profile)

        uow.commit()


def login(
    cmd: commands.LoginCommand,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        user = uow.repo.get(models.User, email=cmd.email)
        if user is None or not user.check_password(cmd.password):
            raise IncorrectCredentials("Incorrect email or password")

        token = user.generate_token()

        return token


def get_user(
    cmd: commands.GetUserCommand,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        user = uow.repo.get(models.User, id=cmd.user_id)
        return {"username": user.username, "email": user.email}


def reset_password(
    cmd: commands.ResetPasswordCommand,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        user = uow.repo.get(models.User, email=cmd.email)
        if user is None or user.username != cmd.username:
            raise IncorrectCredentials("Incorrect email or username")
        new_password = user.reset_password()

        uow.commit()

    return new_password


EVENT_HANDLERS = {
    events.Registered: [create_user_profile],
}  # type: Dict[Type[events.Event], List[Callable]]

COMMAND_HANDLERS = {
    commands.RegisterCommand: register,
    commands.LoginCommand: login,
    commands.GetUserCommand: get_user,
    commands.ResetPasswordCommand: reset_password,
}  # type: Dict[Type[commands.Command], Callable]
