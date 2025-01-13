import re
import pypyodbc as odbc
from werkzeug.security import generate_password_hash

class OpEditProfile:
    def __init__(self, db_connection):
        self.db_connection = db_connection 

    def validate_update_data(self, data):
        allowed_fields = {
            'first_name': None,
            'last_name': None,
            'dob': r'^\d{4}-\d{2}-\d{2}$',  # Validate date format YYYY-MM-DD
            'gender': r'^(Male|Female)$',  # Validate gender
            'job_title': None,
            'phone_number': r'^\+?[0-9\s\-\(\)]+$',  # Phone number validation regex
            'address': None,
            'emergency_contact_name': None,
            'emergency_contact_phone': r'^\+?[0-9\s\-\(\)]+$'
        }

        for field, validation in allowed_fields.items():
            if field in data:
                value = data[field]
                
                if validation and not re.match(validation, value):
                    return False, f"Invalid format for {field}."
        
        return True, "Validation successful."
        

    def update_employee_details(self, data):
        employee_id = data.get('employee_id')
        if not employee_id:
            
            return {"status": "Failure", "message": "Employee ID is required."}

        conn = self.db_connection
        if conn:
            try:
                cursor = conn.cursor()

                # Validate data
                is_valid, validation_message = self.validate_update_data(data)
                if not is_valid:
                    return {"status": "Failure", "message": validation_message}
                # Dynamically create update fields based on provided data
                updates = []
                params = []
                for key, value in data.items():
                    if key in ['first_name', 'last_name', 'dob', 'gender', 'job_title', 'phone_number', 'address', 'emergency_contact_name', 'emergency_contact_phone']:
                        updates.append(f"{key} = ?")
                        params.append(value)
                params.append(employee_id)
            
                if updates:
                    update_clause = ", ".join(updates)
                    query = f"UPDATE Employees SET {update_clause} WHERE employee_id = ?"
                    cursor.execute(query, params)

                    rows_affected = cursor.rowcount
                    if rows_affected == 0:
                        return {"status": "Failure", "message": f"Employee ID '{employee_id}' does not exist."}

                    conn.commit()
                    return {"status": "Success", "message": f"Employee ID '{employee_id}' updated successfully!"}
                else:
                    return {"status": "Failure", "message": "No valid fields to update."}

            except odbc.Error as e:
                conn.rollback()
                return {"status": "Failure", "message": f"Error updating employee details: {str(e)}"}
            finally:
                cursor.close()



    def update_password(self, data):
        """
        Update the password for the user associated with the given employee_id.
        """
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
                hashed_password = generate_password_hash(new_password, method='sha256')
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
