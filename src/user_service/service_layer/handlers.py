from typing import List, Dict, Callable, Type
import string
import random
from user_service.domains import commands, events, models
from user_service.service_layer import unit_of_work
from flask_bcrypt import Bcrypt
import jwt
import pyotp

from user_service.config import SECRET_KEY

bcrypt = Bcrypt()


class EmailExisted(Exception):
    pass


class IncorrectCredentials(Exception):
    pass


class TwoFactorAuthNotEnabled(Exception):
    pass


class InvalidOTP(Exception):
    pass

def random_valid_password(length=12):
    lowercase_letters = string.ascii_lowercase
    uppercase_letters = string.ascii_uppercase
    digits = string.digits
    special_characters = string.punctuation
    all_characters = lowercase_letters + uppercase_letters + digits + special_characters

    password = "".join(random.choice(all_characters) for _ in range(length - 4))
    password += random.choice(lowercase_letters)
    password += random.choice(uppercase_letters)
    password += random.choice(digits)
    password += random.choice(special_characters)

    return password

def register(
    cmd: commands.RegisterCommand,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        user = uow.repo.get(models.User, email=cmd.email)
        if user:
            raise EmailExisted(f"Email {cmd.email} already existed")

        hashed_password = bcrypt.generate_password_hash(cmd.password).decode("utf-8")
        secret_token = pyotp.random_base32()

        user = models.User(cmd.username, cmd.email, hashed_password, secret_token)
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


def enable_two_factor_auth(
    cmd: commands.EnableTwoFactorAuthCommand,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        user = uow.repo.get(models.User, email=cmd.email)
        if user is None:
            raise IncorrectCredentials("Email does not exist")

        otp_code = pyotp.TOTP(user.secret_token).now()
        return otp_code


def verify_enable_two_factor_auth(
    cmd: commands.EnableTwoFactorAuthCommand,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        user = uow.repo.get(models.User, email=cmd.email)
        if user is None:
            raise IncorrectCredentials("Email does not exist")

        if not pyotp.TOTP(user.secret_token).verify(cmd.otp_code):
            raise InvalidOTP("Invalid OTP code")

        user.enable_two_factor_auth()

        uow.commit()


def login(
    cmd: commands.LoginCommand,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        user = uow.repo.get(models.User, email=cmd.email)
        if user is None or not bcrypt.check_password_hash(user.password, cmd.password):
            raise IncorrectCredentials("Incorrect email or password")

        if not user.two_factor_auth_enabled:
            raise TwoFactorAuthNotEnabled(
                "2FA have not been enabled. Please enable first to login."
            )

        token = jwt.encode({"user_id": user.id}, SECRET_KEY, algorithm="HS256")

        return user.id, token


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
        new_password = random_valid_password()
        new_hashed_password = bcrypt.generate_password_hash(new_password).decode("utf-8")
        user.change_password(new_hashed_password)

        uow.commit()

    return new_password


EVENT_HANDLERS = {
    events.Registered: [create_user_profile],
}  # type: Dict[Type[events.Event], List[Callable]]

COMMAND_HANDLERS = {
    commands.RegisterCommand: register,
    commands.EnableTwoFactorAuthCommand: enable_two_factor_auth,
    commands.VerifyEnableTwoFactorAuthCommand: verify_enable_two_factor_auth,
    commands.LoginCommand: login,
    commands.GetUserCommand: get_user,
    commands.ResetPasswordCommand: reset_password,
}  # type: Dict[Type[commands.Command], Callable]
