from flask import Flask, request, jsonify

app = Flask(__name__)

users = []

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    existing_user = next((user for user in users if user['username'] == username), None)

    if existing_user:
        return jsonify({'error': 'Username already taken'}), 400

    new_user = {'username': username, 'password': password}
    users.append(new_user)

    return jsonify({'message': 'User successfully registered'}), 201

if __name__ == '__main__':
    app.run(debug=True)
