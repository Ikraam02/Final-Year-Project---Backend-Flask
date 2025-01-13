import re
import pypyodbc as odbc
from werkzeug.security import generate_password_hash

class OpEditPassword:
    def __init__(self, db_connection):
        self.db_connection = db_connection 

    def update_password(self, data):
        employee_id = data.get('employee_id')
        new_password = data.get('new_password')
        
        if not employee_id:
            return {"status": "Failure", "message": "Employee ID is required."}
        
        if not new_password:
            return {"status": "Failure", "message": "New password is required."}
        
        conn = self.db_connection
        if conn:
            try:
                cursor = conn.cursor()
                
                # Hash the new password using the default method
                hashed_password = generate_password_hash(new_password)
                
                # Update password in the Users table
                query = """
                    UPDATE Users
                    SET password_hash = ?
                    WHERE employee_id = ?
                """
                cursor.execute(query, (hashed_password, employee_id))
                conn.commit()

                return {"status": "Success", "message": "Password updated successfully."}
                
            except odbc.Error as e:
                conn.rollback()
                return {"status": "Failure", "message": f"Error updating password: {str(e)}"}
            finally:
                cursor.close()
