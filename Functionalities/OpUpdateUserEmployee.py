import re
from datetime import datetime

class OpUpdateUserEmployee:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def validate_update_data(self, data):
        """
        Validate the employee update data from the JSON payload.
        Returns a tuple (bool, message). If the first element is False, the validation failed.
        """
        required_fields = [
            'employee_id', 'first_name', 'last_name', 'dob', 'gender',
            'hire_date', 'job_title', 'department_id', 'emergency_contact_name',
            'emergency_contact_phone', 'phone_number', 'address'
        ]

        # Check for missing fields
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"

        # Validate employee_id as a positive integer
        if not isinstance(data['employee_id'], int) or data['employee_id'] <= 0:
            return False, "Employee ID must be a positive integer."

        # Validate first and last names
        if not data['first_name'].strip():
            return False, "First name cannot be empty."
        if not data['last_name'].strip():
            return False, "Last name cannot be empty."

        # Validate date of birth and hire date format
        try:
            datetime.strptime(data['dob'], "%Y-%m-%d")
        except ValueError:
            return False, "Invalid date format for date of birth. Use YYYY-MM-DD."

        try:
            datetime.strptime(data['hire_date'], "%Y-%m-%d")
        except ValueError:
            return False, "Invalid date format for hire date. Use YYYY-MM-DD."

        # Validate gender
        if data['gender'] not in ['Male', 'Female', 'Other']:
            return False, "Gender must be 'Male', 'Female', or 'Other'."

        # Validate department_id as a positive integer
        if not isinstance(data['department_id'], int) or data['department_id'] <= 0:
            return False, "Department ID must be a positive integer."

        # Validate phone numbers
        phone_regex = r'^\+?[0-9\s\-\(\)]+$'  # Allows +, spaces, dashes, and parentheses
        if not re.match(phone_regex, data['phone_number']):
            return False, "Invalid phone number format."
        if not re.match(phone_regex, data['emergency_contact_phone']):
            return False, "Invalid emergency contact phone number format."

        return True, "Validation successful."

    def update_employee(self, data):
        # Validate the incoming data
        is_valid, validation_message = self.validate_update_data(data)
        if not is_valid:
            return {"status": "Failure", "message": validation_message}

        try:
            cursor = self.db_connection.cursor()

            # Extracting data from the JSON payload
            employee_id = data.get('employee_id')
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            dob = data.get('dob')
            gender = data.get('gender')
            hire_date = data.get('hire_date')
            job_title = data.get('job_title')
            department_id = data.get('department_id')
            emergency_contact_name = data.get('emergency_contact_name')
            emergency_contact_phone = data.get('emergency_contact_phone')
            phone_number = data.get('phone_number')
            address = data.get('address')

            # Check if employee exists
            check_employee_query = "SELECT COUNT(*) FROM Employees WHERE employee_id = ?"
            cursor.execute(check_employee_query, (employee_id,))
            exists = cursor.fetchone()[0]

            if exists == 0:
                return {"status": "Failure", "message": "Employee ID does not exist."}

            # SQL query to update the employee details without updating email
            update_query = """
                UPDATE Employees 
                SET first_name = ?, last_name = ?, dob = ?, gender = ?, hire_date = ?, 
                    job_title = ?, department_id = ?, emergency_contact_name = ?, 
                    emergency_contact_phone = ?, phone_number = ?, address = ?
                WHERE employee_id = ?
            """

            # Execute the query with data from the request
            cursor.execute(update_query, (first_name, last_name, dob, gender, hire_date,
                                          job_title, department_id, emergency_contact_name,
                                          emergency_contact_phone, phone_number, address,
                                          employee_id))
            self.db_connection.commit()  # Commit the transaction

            return {"status": "Success", "message": "Employee updated successfully."}

        except Exception as e:
            self.db_connection.rollback()  # Roll back any changes if an error occurs
            return {"status": "Failure", "message": f"Error updating employee: {str(e)}"}

        finally:
            cursor.close()  # Close the cursor
