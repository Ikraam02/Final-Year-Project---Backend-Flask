import pypyodbc as odbc
from datetime import datetime
from werkzeug.security import generate_password_hash

class OpManageUsers:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def create_user(self, user_data):
        """
        Create a new user in the Users table.
        :param user_data: Dictionary containing user details.
        """
        try:
            cursor = self.db_connection.cursor()
            insert_query = """
                INSERT INTO Users (username, password_hash, role_id, email, last_login, employee_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(insert_query, (
                user_data['username'],
                user_data['password_hash'],
                user_data['role_id'],
                user_data['email'],
                user_data['last_login'],
                user_data['employee_id']
            ))
            self.db_connection.commit()
            return {"status": "Success", "message": "User created successfully."}

        except odbc.Error as e:
            self.db_connection.rollback()
            return {"status": "Failure", "message": f"Error creating user: {str(e)}"}

        finally:
            cursor.close()

    def read_user(self, employee_id):
        """
        Retrieve user details by employee_id.
        :param employee_id: The employee ID to look up.
        """
        try:
            cursor = self.db_connection.cursor()
            query = "SELECT * FROM Users WHERE employee_id = ?"
            cursor.execute(query, (employee_id,))
            user = cursor.fetchone()

            if user:
                user_data = {
                    "user_id": user[0],
                    "username": user[1],
                    "password_hash": user[2],
                    "role_id": user[3],
                    "email": user[4],
                    "last_login": user[5],
                    "employee_id": user[6]
                }
                return {"status": "Success", "data": user_data}
            else:
                return {"status": "Failure", "message": "User not found."}

        except odbc.Error as e:
            return {"status": "Failure", "message": f"Error retrieving user: {str(e)}"}

        finally:
            cursor.close()

    def update_user(self, employee_id, user_data):
        """
        Update user details based on employee_id.
        :param employee_id: The employee ID of the user to update.
        :param user_data: Dictionary containing fields to update.
        """
        try:
            cursor = self.db_connection.cursor()
            
            # Constructing dynamic update query based on provided fields
            update_query = "UPDATE Users SET"
            params = []
            
            if 'last_login' in user_data:
                update_query += " last_login = ?,"
                params.append(user_data['last_login'])
            
            if 'username' in user_data:
                update_query += " username = ?,"
                params.append(user_data['username'])
                
            if 'password_hash' in user_data:
                password_hash = self.hash_password(user_data.get('password_hash'))
                update_query += " password_hash = ?,"
                params.append(password_hash)
                
            if 'role_id' in user_data:
                update_query += " role_id = ?,"
                params.append(user_data['role_id'])
                
            if 'email' in user_data:
                update_query += " email = ?,"
                params.append(user_data['email'])
                
            if 'employee_id' in user_data:
                update_query += " employee_id = ?,"
                params.append(user_data['employee_id'])

            # Removing trailing comma and adding WHERE clause
            update_query = update_query.rstrip(",") + " WHERE employee_id = ?"
            params.append(employee_id)

            cursor.execute(update_query, tuple(params))
            self.db_connection.commit()

            if cursor.rowcount > 0:
                return {"status": "Success", "message": "User updated successfully."}
            else:
                return {"status": "Failure", "message": "No user found with the given employee_id."}

        except odbc.Error as e:
            self.db_connection.rollback()
            return {"status": "Failure", "message": f"Error updating user: {str(e)}"}

        finally:
            cursor.close()

    def delete_user(self, employee_id):
        """
        Delete a user from the Users table based on employee_id.
        :param employee_id: The employee ID of the user to delete.
        """
        try:
            cursor = self.db_connection.cursor()
            delete_query = "DELETE FROM Users WHERE employee_id = ?"
            cursor.execute(delete_query, (employee_id,))
            self.db_connection.commit()

            if cursor.rowcount > 0:
                return {"status": "Success", "message": "User deleted successfully."}
            else:
                return {"status": "Failure", "message": "No user found with the given employee_id."}

        except odbc.Error as e:
            self.db_connection.rollback()
            return {"status": "Failure", "message": f"Error deleting user: {str(e)}"}

        finally:
            cursor.close()
