from flask import Flask, request, jsonify, blueprints

from user_service import bootstrap
from user_service.domains import commands
from user_service.service_layer.handlers import (
    InvalidPassword,
    EmailExisted,
    IncorrectCredentials,
    UnathorizedAccess,
)

bp = blueprints.Blueprint("user", __name__)
bus = bootstrap.bootstrap()


@bp.route("/register", methods=["POST"])
def register():
    try:
        body = request.json
        cmd = commands.RegisterCommand(**body)
        bus.handle(cmd)
    except InvalidPassword as e:
        return jsonify({"error": str(e)}), 400

    except EmailExisted as e:
        return jsonify({"error": str(e)}), 409

    return jsonify({"message": "User successfully registered"}), 201


@bp.route("/login", methods=["POST"])
def login():
    try:
        body = request.json
        cmd = commands.LoginCommand(**body)
        token = bus.handle(cmd)

    except IncorrectCredentials as e:
        return jsonify({"error": str(e)}), 401

    return jsonify({"token": token}), 200


@bp.route("/user/<string:user_id>", methods=["GET"])
def get_user(user_id):
    try:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        cmd = commands.GetUserCommand(user_id, token)
        user = bus.handle(cmd)
    except UnathorizedAccess as e:
        return jsonify({"error": str(e)}), 401

    return jsonify({"user": user}), 200


@bp.route("/reset-password", methods=["POST"])
def reset_password():
    try:
        body = request.json
        cmd = commands.ResetPasswordCommand(**body)
        new_password = bus.handle(cmd)
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
