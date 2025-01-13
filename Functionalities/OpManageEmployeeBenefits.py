import pypyodbc as odbc

class OpManageEmployeeBenefits:
    def __init__(self, db_connection):
        self.db_connection = db_connection  # Store the database connection

    def add_employee_benefit(self, data):
        """Add a new employee benefit to the EmployeeBenefits table."""
        required_fields = ['employee_id', 'benefit_id', 'start_date', 'end_date']

        # Check for missing fields
        for field in required_fields:
            if field not in data:
                return {"status": "Failure", "message": f"Missing required field: {field}"}

        try:
            cursor = self.db_connection.cursor()

            # Check if the employee_id exists in the Employees table
            check_employee_query = "SELECT COUNT(*) FROM Employees WHERE employee_id = ?"
            cursor.execute(check_employee_query, (data['employee_id'],))
            existing_employee_count = cursor.fetchone()[0]

            if existing_employee_count == 0:
                return {"status": "Failure", "message": f"Employee with ID '{data['employee_id']}' does not exist."}

            # Check if the benefit_id exists in the Benefits table
            check_benefit_query = "SELECT COUNT(*) FROM Benefits WHERE benefit_id = ?"
            cursor.execute(check_benefit_query, (data['benefit_id'],))
            existing_benefit_count = cursor.fetchone()[0]

            if existing_benefit_count == 0:
                return {"status": "Failure", "message": f"Benefit with ID '{data['benefit_id']}' does not exist."}

            # Insert a new employee benefit into the EmployeeBenefits table
            insert_query = """
                INSERT INTO EmployeeBenefits (employee_id, benefit_id, start_date, end_date)
                VALUES (?, ?, ?, ?)
            """
            cursor.execute(insert_query, (
                data['employee_id'],
                data['benefit_id'],
                data['start_date'],
                data['end_date']
            ))
            self.db_connection.commit()  # Commit the transaction

            return {"status": "Success", "message": "Employee benefit added successfully."}

        except odbc.Error as e:
            self.db_connection.rollback()  # Roll back any changes if an error occurs
            return {"status": "Failure", "message": f"Error adding employee benefit: {str(e)}"}

        finally:
            cursor.close()  # Close the cursor

    def update_employee_benefit(self, data):
        """Update an existing employee benefit in the EmployeeBenefits table."""
        employee_benefit_id = data.get('employee_benefit_id')
        employee_id = data.get('employee_id')
        benefit_id = data.get('benefit_id')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if not employee_benefit_id:
            return {"status": "Failure", "message": "Employee Benefit ID is required."}

        try:
            cursor = self.db_connection.cursor()

            # Dynamically build the SQL update query
            update_query = "UPDATE EmployeeBenefits SET "
            update_fields = []
            update_values = []

            if employee_id:
                update_fields.append("employee_id = ?")
                update_values.append(employee_id)
            if benefit_id:
                update_fields.append("benefit_id = ?")
                update_values.append(benefit_id)
            if start_date:
                update_fields.append("start_date = ?")
                update_values.append(start_date)
            if end_date:
                update_fields.append("end_date = ?")
                update_values.append(end_date)

            update_query += ", ".join(update_fields)
            update_query += " WHERE employee_benefit_id = ?"
            update_values.append(employee_benefit_id)

            cursor.execute(update_query, tuple(update_values))
            self.db_connection.commit()  # Commit the transaction

            if cursor.rowcount > 0:
                return {"status": "Success", "message": "Employee benefit updated successfully."}
            else:
                return {"status": "Failure", "message": "No employee benefit found for the provided Employee Benefit ID."}

        except odbc.Error as e:
            self.db_connection.rollback()  # Roll back any changes if an error occurs
            return {"status": "Failure", "message": f"Error updating employee benefit: {str(e)}"}

        finally:
            cursor.close()  # Close the cursor

    def delete_employee_benefit(self, data):
        """Delete an employee benefit from the EmployeeBenefits table."""
        employee_benefit_id = data.get('employee_benefit_id')

        if not employee_benefit_id:
            return {"status": "Failure", "message": "Employee Benefit ID is required."}

        try:
            cursor = self.db_connection.cursor()

            # Delete the employee benefit from the EmployeeBenefits table
            delete_query = """
                DELETE FROM EmployeeBenefits WHERE employee_benefit_id = ?
            """
            cursor.execute(delete_query, (employee_benefit_id,))
            self.db_connection.commit()  # Commit the transaction

            if cursor.rowcount > 0:
                return {"status": "Success", "message": "Employee benefit deleted successfully."}
            else:
                return {"status": "Failure", "message": "No employee benefit found for the provided Employee Benefit ID."}

        except odbc.Error as e:
            self.db_connection.rollback()  # Roll back any changes if an error occurs
            return {"status": "Failure", "message": f"Error deleting employee benefit: {str(e)}"}

        finally:
            cursor.close()  # Close the cursor

    def get_employee_benefit(self, data):
        """Retrieve details of a specific employee benefit from the EmployeeBenefits table."""
        employee_benefit_id = data.get('employee_benefit_id')

        if not employee_benefit_id:
            return {"status": "Failure", "message": "Employee Benefit ID is required."}

        try:
            cursor = self.db_connection.cursor()

            # Query to get the employee benefit details
            query = """
                SELECT employee_benefit_id, employee_id, benefit_id, start_date, end_date
                FROM EmployeeBenefits
                WHERE employee_benefit_id = ?
            """
            cursor.execute(query, (employee_benefit_id,))
            result = cursor.fetchone()

            if result:
                benefit_details = {
                    "employee_benefit_id": result[0],
                    "employee_id": result[1],
                    "benefit_id": result[2],
                    "start_date": result[3],
                    "end_date": result[4]
                }
                return {"status": "Success", "data": benefit_details}
            else:
                return {"status": "Failure", "message": "No employee benefit found for the provided Employee Benefit ID."}

        except odbc.Error as e:
            return {"status": "Failure", "message": f"Error retrieving employee benefit: {str(e)}"}

        finally:
            cursor.close()  # Close the cursor

    def get_all_employee_benefits(self):
        """Retrieve all employee benefits from the EmployeeBenefits table."""
        try:
            cursor = self.db_connection.cursor()

            # Query to get all employee benefits
            query = """
                SELECT employee_benefit_id, employee_id, benefit_id, start_date, end_date
                FROM EmployeeBenefits
            """
            cursor.execute(query)
            results = cursor.fetchall()

            benefits = []
            for result in results:
                benefits.append({
                    "employee_benefit_id": result[0],
                    "employee_id": result[1],
                    "benefit_id": result[2],
                    "start_date": result[3],
                    "end_date": result[4]
                })

            return {"status": "Success", "data": benefits}

        except odbc.Error as e:
            return {"status": "Failure", "message": f"Error retrieving employee benefits: {str(e)}"}

        finally:
            cursor.close()  # Close the cursor
