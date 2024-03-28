from flask import Flask, request, jsonify, blueprints
import string
import jwt

from user_service import bootstrap
from user_service.domains import commands
from user_service.service_layer.handlers import (
    EmailExisted,
    IncorrectCredentials,
)
from user_service.config import SECRET_KEY

bp = blueprints.Blueprint("user", __name__)
bus = bootstrap.bootstrap()


class InvalidPassword(Exception):
    pass


class UnathorizedAccess(Exception):
    pass


def validate_password(password: str):
    # Minimum length
    if len(password) < 8:
        raise InvalidPassword("Invalid password")

    # No spaces
    if " " in password:
        raise InvalidPassword("Invalid password")

    # At least one digit
    if not any(c.isdigit() for c in password):
        raise InvalidPassword("Invalid password")

    # At least one special character
    if not any(c in string.punctuation for c in password):
        raise InvalidPassword("Invalid password")

    return True


def validate_token(token, user_id):
    if not token:
        raise UnathorizedAccess("Authorization token missing")

    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        authenticated_user_id = decoded_token.get("user_id")

        if authenticated_user_id != user_id:
            raise UnathorizedAccess("Unauthorized access to user account")

    except jwt.InvalidTokenError:
        raise UnathorizedAccess("Invalid token")


@bp.route("/register", methods=["POST"])
def register():
    try:
        body = request.json
        validate_password(body["password"])

    except InvalidPassword as e:
        return jsonify({"error": str(e)}), 400

    try:
        cmd = commands.RegisterCommand(**body)
        bus.handle(cmd)

    except EmailExisted as e:
        return jsonify({"error": str(e)}), 409

    return jsonify({"message": "User successfully registered"}), 201


@bp.route("/login", methods=["POST"])
def login():
    try:
        body = request.json
        cmd = commands.LoginCommand(**body)
        results = bus.handle(cmd)
        token = results[0]

    except IncorrectCredentials as e:
        return jsonify({"error": str(e)}), 401

    return jsonify({"token": token}), 200


@bp.route("/user/<string:user_id>", methods=["GET"])
def get_user(user_id):
    try:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        validate_token(token, user_id)

    except UnathorizedAccess as e:
        return jsonify({"error": str(e)}), 401

    try:
        cmd = commands.GetUserCommand(user_id, token)
        results = bus.handle(cmd)
        user = results[0]

    except UnathorizedAccess as e:
        return jsonify({"error": str(e)}), 401

    return jsonify({"user": user}), 200


@bp.route("/reset-password", methods=["POST"])
def reset_password():
    try:
        body = request.json
        cmd = commands.ResetPasswordCommand(**body)
        results = bus.handle(cmd)
        new_password = results[0]

    except IncorrectCredentials as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"new_password": new_password}), 200


def create_app():
    app = Flask(__name__)
    app.register_blueprint(bp)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
