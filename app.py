from flask import Flask, request, jsonify
from OpCode.users import Users  # Import the Users class


app = Flask(__name__)


# Initialize the Users class with a connection string
connection_string = """
    DRIVER={SQL SERVER};
    SERVER=DESKTOP-G4A2LDV;
    DATABASE=HRMS;
    Trust_Connection=yes;
"""
users = Users(connection_string)

# Route for handling incoming JSON requests
@app.route('/process', methods=['POST'])
def process_request():
    data = request.json

    # Validate the incoming JSON request
    if 'operationCode' not in data:
        return jsonify({
            "status": "Failure",
            "message": "Missing operation code."
        }), 400

    operation_code = data['operationCode']

    # Route based on operation code
    try:
        if operation_code == "OpCreateUser":
            # Extract necessary fields from data and call the method
            response = users.create_user(
                username=data['username'],
                password_hash=data['password_hash'],
                role_id=data['role_id'],
                email=data['email'],
                employee_id=data.get('employee_id')
            )
            result = {"status": "Success", "message": "User created successfully."}
        elif operation_code == "OpUpdateEmployeeDetails":
            response = users.update_user(  # Example usage, modify fields as needed
                user_id=data['user_id'],
                username=data.get('username'),
                password_hash=data.get('password_hash'),
                role_id=data.get('role_id'),
                email=data.get('email'),
                last_login=data.get('last_login'),
                employee_id=data.get('employee_id')
            )
            result = {"status": "Success", "message": "Employee details updated successfully."}
        elif operation_code == "OpDeleteUser":
            response = users.delete_user(data['user_id'])
            result = {"status": "Success", "message": "User deleted successfully."}
        else:
            return jsonify({
                "status": "Failure",
                "message": f"Unsupported operation code: {operation_code}"
            }), 400

        return jsonify(result), 200  # Respond back with the result from service functions

    except Exception as e:
        return jsonify({
            "status": "Failure",
            "message": str(e)
        }), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
