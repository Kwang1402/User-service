from flask import Flask, request, jsonify, blueprints

from user_service import bootstrap
from user_service.domains import commands
from user_service.service_layer.handlers import InvalidPassword, EmailExisted

bp = blueprints.Blueprint("user", __name__)
bus = bootstrap.bootstrap()


@bp.route("/register", methods=["POST"])
def register():
    try:
        body = request.json
        cmd = commands.RegisterCommand(**body)
        bus.handle(cmd)
    except (InvalidPassword, EmailExisted) as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"message": "User successfully registered"}), 201


def create_app():
    app = Flask(__name__)
    app.register_blueprint(bp)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
