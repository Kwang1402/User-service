import pytest
from typing import Type
from flask_bcrypt import Bcrypt
from user_service import bootstrap
import pyotp
import time
from user_service.adapters import repository
from user_service.service_layer import unit_of_work
from user_service.domains import models, commands
from user_service.service_layer.handlers import event
from tests import random_refs

bcrypt = Bcrypt()


class FakeRepository(repository.AbstractRepository):
    def __init__(self, models):
        super().__init__()
        self._models = set(models)

    def _add(self, model):
        self._models.add(model)

    def _get(
        self,
        model: Type[models.BaseModel],
        *args,
        **kwargs,
    ) -> Type[models.BaseModel]:
        for m in self._models:
            if isinstance(m, model) and all(
                getattr(m, key) == value for key, value in kwargs.items()
            ):
                return m
        return None


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.repo = FakeRepository([])
        self.committed = False

    def _commit(self):
        self.committed = True

    def rollback(self):
        pass

    def close(self):
        pass


def bootstrap_test_app():
    return bootstrap.bootstrap(
        start_orm=False,
        uow=FakeUnitOfWork,
    )


class TestRegister:
    def test_register(self, data):
        bus = bootstrap_test_app()
        bus.handle(commands.RegisterCommand(**data))
        user = bus.uow.repo.get(models.User, email=data["email"])

        assert user is not None
        assert user.username == data["username"]
        assert user.email == data["email"]
        assert bcrypt.check_password_hash(user.password, data["password"])

        profile = bus.uow.repo.get(models.Profile, user_id=user.id)
        assert profile.backup_email == data["backup_email"]
        assert profile.gender == data["gender"]
        assert profile.date_of_birth == data["date_of_birth"]

    def test_email_already_existed(self, data, data2):
        bus = bootstrap_test_app()
        bus.handle(commands.RegisterCommand(**data))

        data2["email"] = data["email"]
        with pytest.raises(
            event.EmailExisted, match=f"Email {data2['email']} already existed"
        ):
            bus.handle(commands.RegisterCommand(**data2))


class TestEnableAndVerify2FA:
    def test_enable_and_verify_2fa(self, data):
        bus = bootstrap_test_app()
        bus.handle(commands.RegisterCommand(**data))

        results = bus.handle(commands.EnableTwoFactorAuthCommand(data["email"]))
        otp_code = results[0]
        assert otp_code is not None

        bus.handle(commands.VerifyEnableTwoFactorAuthCommand(data["email"], otp_code))
        user = bus.uow.repo.get(models.User, email=data["email"])

        assert user.two_factor_auth_enabled == True

    def test_enable_2fa_email_does_not_exist(self, data):
        bus = bootstrap_test_app()
        with pytest.raises(event.IncorrectCredentials, match="Email does not exist"):
            bus.handle(commands.EnableTwoFactorAuthCommand(data["email"]))

    def test_verify_2fa_email_does_not_exist(self, data):
        bus = bootstrap_test_app()

        otp_code = pyotp.TOTP(pyotp.random_base32()).now()
        with pytest.raises(event.IncorrectCredentials, match="Email does not exist"):
            bus.handle(
                commands.VerifyEnableTwoFactorAuthCommand(data["email"], otp_code)
            )

    def test_verify_2fa_incorrect_code(self, data):
        bus = bootstrap_test_app()
        bus.handle(commands.RegisterCommand(**data))

        otp_code = pyotp.TOTP(pyotp.random_base32()).now()
        with pytest.raises(event.InvalidOTP, match="Invalid OTP code"):
            bus.handle(
                commands.VerifyEnableTwoFactorAuthCommand(data["email"], otp_code)
            )

        user = bus.uow.repo.get(models.User, email=data["email"])

        assert user.two_factor_auth_enabled == False

    def test_verify_2fa_expired_code(self, data):
        bus = bootstrap_test_app()
        bus.handle(commands.RegisterCommand(**data))

        results = bus.handle(commands.EnableTwoFactorAuthCommand(data["email"]))
        otp_code = results[0]

        time.sleep(30)
        with pytest.raises(event.InvalidOTP, match="Invalid OTP code"):
            bus.handle(
                commands.VerifyEnableTwoFactorAuthCommand(data["email"], otp_code)
            )

        user = bus.uow.repo.get(models.User, email=data["email"])

        assert user.two_factor_auth_enabled == False


class TestLogin:
    def test_login(self, data):
        bus = bootstrap_test_app()
        bus.handle(commands.RegisterCommand(**data))

        results = bus.handle(commands.EnableTwoFactorAuthCommand(data["email"]))
        otp_code = results[0]

        bus.handle(commands.VerifyEnableTwoFactorAuthCommand(data["email"], otp_code))

        results = bus.handle(commands.LoginCommand(data["email"], data["password"]))

        token = results[0]
        assert token is not None

    def test_incorrect_email(self):
        bus = bootstrap_test_app()

        with pytest.raises(
            event.IncorrectCredentials, match="Incorrect email or password"
        ):
            bus.handle(
                commands.LoginCommand(
                    random_refs.random_email(), random_refs.random_valid_password()
                )
            )

    def test_incorrect_password(self, data):
        bus = bootstrap_test_app()

        bus.handle(commands.RegisterCommand(**data))

        with pytest.raises(
            event.IncorrectCredentials, match="Incorrect email or password"
        ):
            bus.handle(
                commands.LoginCommand(
                    data["email"], random_refs.random_valid_password()
                )
            )


class TestGetUser:
    def test_get_user(self, data):
        bus = bootstrap_test_app()

        bus.handle(commands.RegisterCommand(**data))
        results = bus.handle(commands.EnableTwoFactorAuthCommand(data["email"]))
        otp_code = results[0]

        bus.handle(commands.VerifyEnableTwoFactorAuthCommand(data["email"], otp_code))

        results = bus.handle(commands.LoginCommand(data["email"], data["password"]))
        user_id, token = results[0]
        user = bus.uow.repo.get(models.User, email=data["email"])

        results = bus.handle(commands.GetUserCommand(user_id, token))

        user_info = results[0]
        assert user_info == {"username": user.username, "email": user.email}


class TestResetPassword:
    def test_reset_password(self, data):
        bus = bootstrap_test_app()

        bus.handle(commands.RegisterCommand(**data))
        results = bus.handle(
            commands.ResetPasswordCommand(data["email"], data["username"])
        )

        new_password = results[0]
        user = bus.uow.repo.get(models.User, email=data["email"])

        assert bcrypt.check_password_hash(user.password, new_password)

    def test_incorrect_email(self):
        bus = bootstrap_test_app()

        with pytest.raises(
            event.IncorrectCredentials, match="Incorrect email or username"
        ):
            bus.handle(
                commands.ResetPasswordCommand(
                    random_refs.random_email(), random_refs.random_username()
                )
            )

    def test_incorrect_username(self, data):
        bus = bootstrap_test_app()
        bus.handle(commands.RegisterCommand(**data))

        with pytest.raises(
            event.IncorrectCredentials, match="Incorrect email or username"
        ):
            bus.handle(
                commands.ResetPasswordCommand(
                    data["email"], random_refs.random_username()
                )
            )
