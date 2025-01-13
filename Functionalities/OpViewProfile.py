import pypyodbc as odbc  # Import pypyodbc for database operations

class OpViewProfile:
    def __init__(self, db_connection):
        self.db_connection = db_connection  # Store the database connection

    def validate_employee_id(self, data):

        employee_id = data.get('employee_id')
        print("employee_id: ", employee_id)
        if not employee_id:
            return False, "Employee ID is required."
        if not isinstance(employee_id, int) or employee_id <= 0:
            return False, "Invalid Employee ID. It must be a positive integer."
        return True, "Validation successful."

    def view_profile(self, data):
    # Validate the incoming data for employee_id
        is_valid, validation_message = self.validate_employee_id(data)
        if not is_valid:
            print(validation_message)
            return {"status": "Failure", "message": validation_message}

        employee_id = data.get('employee_id')

        try:
            cursor = self.db_connection.cursor()

            # Query to retrieve details from the Employees table
            query = """
                SELECT 
                    employee_id, first_name, last_name, dob, gender, hire_date, 
                    job_title, emergency_contact_name, emergency_contact_phone, 
                    email, phone_number, address
                FROM Employees
                WHERE employee_id = ?
            """
            cursor.execute(query, (employee_id,))
            result = cursor.fetchone()

            if result:
                # Map the result to a dictionary
                profile_details = {
                    "employee_id": result[0],
                    "first_name": result[1],
                    "last_name": result[2],
                    "dob": result[3],
                    "gender": result[4],
                    "hire_date": result[5],
                    "job_title": result[6],
                    "emergency_contact_name": result[7],
                    "emergency_contact_phone": result[8],
                    "email": result[9],
                    "phone_number": result[10],
                    "address": result[11],
                }
                print("Profile Details: ", profile_details)
                return {"status": "Success", "data": profile_details}
            else:
                print("Employee Not found Details: ")
                return {"status": "Failure", "message": "Employee not found."}

        except odbc.Error as e:
            return {"status": "Failure", "message": f"Error retrieving profile details: {str(e)}"}
        finally:
            cursor.close()  # Close the cursor

