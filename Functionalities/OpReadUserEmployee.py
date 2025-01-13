import pypyodbc as odbc  # Import pypyodbc for database operations

class OpGetEmployeeById:
    def __init__(self, db_connection):
        self.db_connection = db_connection  # Store the database connection

    def get_employee_by_id(self, data):
        employee_id = data.get('employee_id')  # Extract employee_id from the data dictionary
        
        if not employee_id:
            return {"status": "Failure", "message": "Employee ID is required."}
        try:
            cursor = self.db_connection.cursor()

            # Query to retrieve employee details for the provided employee_id
            query = """
                SELECT 
                    employee_id, first_name, last_name, dob, gender, hire_date, 
                    job_title, department_id, emergency_contact_name, emergency_contact_phone, 
                    email, phone_number, address
                FROM Employees
                WHERE employee_id = ?
            """
            cursor.execute(query, [employee_id])
            result = cursor.fetchone()

            # Check if the query returned a result
            if result:
                # Map the result to a dictionary
                employee_details = {
                    "employee_id": result[0],
                    "first_name": result[1],
                    "last_name": result[2],
                    "dob": result[3],
                    "gender": result[4],
                    "hire_date": result[5],
                    "job_title": result[6],
                    "department_id": result[7],
                    "emergency_contact_name": result[8],
                    "emergency_contact_phone": result[9],
                    "email": result[10],
                    "phone_number": result[11],
                    "address": result[12]
                }
                return {"status": "Success", "data": employee_details}
            else:
                return {"status": "Failure", "message": "Employee not found."}

        except odbc.Error as e:
            return {"status": "Failure", "message": f"Error retrieving employee: {str(e)}"}
        finally:
            cursor.close()  # Close the cursor
