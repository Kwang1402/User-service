from flask import Flask, request, jsonify
from marshmallow import Schema, fields

app = Flask(__name__)

users = []

class RegistrationSchema(Schema):
    username = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.String(required=True)
    reconfirm_password = fields.String(required=True)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    try:
        registration_data = RegistrationSchema().load(data)
    except Exception as e:
        return  jsonify({'error': str(e)}), 400
    
    existing_user = next((user for user in users if user['username'] == registration_data['username']), None)

    if existing_user:
        return jsonify({'error': 'Username already taken'}), 400

    existing_email = next((user for user in users if user['email'] == registration_data['email']), None)

    if existing_email:
        return jsonify({'error': 'Email already used'}), 400

    if(registration_data['password'] != registration_data['reconfirm_password']):
        return jsonify({'error': 'Passwords do not match'}), 400
    
    new_user = {
        'username': registration_data['username'], 
        'password': registration_data['password'], 
        'email': registration_data['email']
    }
    
    users.append(new_user)

    return jsonify({'message': 'User successfully registered'}), 201

if __name__ == '__main__':
    app.run(debug=True)
