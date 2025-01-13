import pypyodbc as odbc  # Import pypyodbc for database operations
from werkzeug.security import check_password_hash
from datetime import datetime

class OpLogin:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def authenticate_user(self, data):
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return {"status": "Failure", "message": "Username and password are required."}

        # Special case for Super HR login
        if username == "username" and password == "password":
            return {"status": "Success", "message": "Authentication successful.", "role": "SuperHR"}

        try:
            cursor = self.db_connection.cursor()

            # Query to retrieve the user details from the Users table
            user_query = """
                SELECT u.username, u.password_hash, u.employee_id, r.description
                FROM Users u
                JOIN Roles r ON u.role_id = r.role_id
                WHERE u.username = ?
            """
            cursor.execute(user_query, (username,))
            result = cursor.fetchone()

            if result:
                stored_password_hash = result[1]
                employee_id = result[2]
                role_description = result[3]

                # Use werkzeug's check_password_hash to verify the password
                if check_password_hash(stored_password_hash, password):
                    # Authentication successful, update last_login field
                    update_last_login_query = """
                        UPDATE Users 
                        SET last_login = ?
                        WHERE employee_id = ?
                    """
                    current_datetime = datetime.now()
                    cursor.execute(update_last_login_query, (current_datetime, employee_id))
                    self.db_connection.commit()

                    # Check role description to determine the user type
                    if role_description == "Human Resource":
                        return {"status": "Success", "message": "Authentication successful.", "role": "HR", "employee_id": employee_id}
                    else:
                        return {"status": "Success", "message": "Authentication successful.", "role": "Employee", "employee_id": employee_id}
                else:
                    return {"status": "Failure", "message": "Invalid password."}
            else:
                return {"status": "Failure", "message": "Username not found."}

        except odbc.Error as e:
            self.db_connection.rollback()
            return {"status": "Failure", "message": f"Error authenticating user: {str(e)}"}

        finally:
            cursor.close()
