from flask import Flask, request, jsonify

from user_service import bootstrap
from user_service.domains import commands
from user_service.service_layer.handlers import InvalidPassword, EmailExisted

app = Flask(__name__)
bus = bootstrap.bootstrap()


@app.route("/register", methods=["POST"])
def register():
    try:
        body = request.json
        cmd = commands.Register(
            **body
            # request.json["username"],
            # request.json["email"],
            # request.json["password"],
            # request.json["backup_email"],
            # request.json["gender"],
            # request.json["date_of_birth"],
        )
        bus.handle(cmd)
    except (InvalidPassword, EmailExisted) as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"message": "User successfully registered"}), 201


if __name__ == "__main__":
    app.run(debug=True)
