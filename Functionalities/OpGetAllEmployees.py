import pypyodbc as odbc  # Import pypyodbc for database operations

class OpGetAllEmployees:
    def __init__(self, db_connection):
        self.db_connection = db_connection  # Store the database connection

    def view_all_employees(self):
        try:
            cursor = self.db_connection.cursor()

            # Query to retrieve all details from the Employees table
            query = """
                SELECT 
                    employee_id, first_name, last_name, dob, gender, hire_date, 
                    job_title, department_id, emergency_contact_name, emergency_contact_phone, 
                    email, phone_number, address
                FROM Employees
            """
            cursor.execute(query)
            results = cursor.fetchall()

            # Check if the query returned any results
            if results:
                # Map the results to a list of dictionaries
                employees = []
                for row in results:
                    employee_details = {
                        "employee_id": row[0],
                        "first_name": row[1],
                        "last_name": row[2],
                        "dob": row[3],
                        "gender": row[4],
                        "hire_date": row[5],
                        "job_title": row[6],
                        "department_id": row[7],
                        "emergency_contact_name": row[8],
                        "emergency_contact_phone": row[9],
                        "email": row[10],
                        "phone_number": row[11],
                        "address": row[12]
                    }
                    employees.append(employee_details)
                return {"status": "Success", "data": employees}
            else:
                return {"status": "Failure", "message": "No employees found."}

        except odbc.Error as e:
            return {"status": "Failure", "message": f"Error retrieving employees: {str(e)}"}
        finally:
            cursor.close()  # Close the cursor
