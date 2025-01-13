import re  # Import the regex module for email validation
import hashlib  # Import hashlib for hashing passwords
from werkzeug.security import generate_password_hash

class OpAddUserEmployee:
    def __init__(self, db_connection):
        self.db_connection = db_connection  # Store the database connection

    def validate_user_data(self, data):
        required_fields = ['username', 'password_hash', 'role_id', 'email']

        # Check for missing fields
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"

        # Check if username is not empty
        if not data['username']:
            return False, "Username cannot be empty."

        # Check if password_hash is not empty
        if not data['password_hash']:
            return False, "Password hash cannot be empty."

        # Check if role_id is a positive integer
        if not isinstance(data['role_id'], int) or data['role_id'] <= 0:
            return False, "Role ID must be a positive integer."

        # Validate the email format using regex
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, data['email']):
            return False, "Invalid email format."

        return True, "Validation successful."

    def hash_password(self, password):
        return generate_password_hash(password)

    def check_username_exists(self, username):
        """
        Check if the username already exists in the Users table.
        Returns True if the username exists, False otherwise.
        """
        try:
            cursor = self.db_connection.cursor()
            check_query = "SELECT COUNT(*) FROM Users WHERE username = ?"
            cursor.execute(check_query, (username,))
            result = cursor.fetchone()[0]
            return result > 0  # Returns True if username exists, False otherwise
        finally:
            cursor.close()

    def check_email_exists(self, email):
        try:
            cursor = self.db_connection.cursor()
            check_query = "SELECT COUNT(*) FROM Users WHERE email = ?"
            cursor.execute(check_query, (email,))
            result = cursor.fetchone()[0]
            return result > 0  # Returns True if username exists, False otherwise
        finally:
            cursor.close()

    def add_user(self, data):
        # Validate the incoming user data
        is_valid, validation_message = self.validate_user_data(data)
        if not is_valid:
            return {"status": "Failure", "message": validation_message}

        # Check if the username already exists
        if self.check_username_exists(data['username']):
            return {"status": "Failure", "message": "Username already exists. Please choose a different username."}
        
        if self.check_email_exists(data['email']):
            return {"status": "Failure", "message": "Email already exists. Please enter a different email."}

        try:
            cursor = self.db_connection.cursor()

            # Extracting the data from the JSON payload and hashing the password
            username = data.get('username')
            password_hash = self.hash_password(data.get('password_hash'))
            role_id = data.get('role_id')
            email = data.get('email')

            # Step 1: Insert into Employees table
            insert_employee_query = """
                INSERT INTO Employees (email)
                VALUES (?)
            """
            cursor.execute(insert_employee_query, (email,))
            self.db_connection.commit()

            # Retrieve the newly generated employee_id
            cursor.execute("SELECT @@IDENTITY AS employee_id")
            employee_id = cursor.fetchone()[0]

            # Step 2: Insert into Users table
            insert_user_query = """
                INSERT INTO Users (username, password_hash, role_id, email, employee_id)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(insert_user_query, (username, password_hash, role_id, email, employee_id))
            self.db_connection.commit()  # Commit the transaction

            return {"status": "Success", "message": "User added successfully."}

        except Exception as e:
            self.db_connection.rollback()  # Roll back any changes if an error occurs
            return {"status": "Failure", "message": f"Error adding user: {str(e)}"}

        finally:
            cursor.close()  # Close the cursor
