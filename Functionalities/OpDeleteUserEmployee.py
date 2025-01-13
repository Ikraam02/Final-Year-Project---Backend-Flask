import pypyodbc as odbc

class OpDeleteUserEmployee:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def delete_employee(self, data):
        """
        Delete employee and associated user based on the employee_id from the JSON data.
        """
        employee_id = data.get('employee_id')
        if not employee_id:
            return {"status": "Failure", "message": "Employee ID is required."}

        conn = self.db_connection
        if conn:
            try:
                cursor = conn.cursor()

                # Begin a transaction
                conn.autocommit = False

                # Delete from Users table
                delete_user_query = "DELETE FROM Users WHERE employee_id = ?"
                cursor.execute(delete_user_query, (employee_id,))

                # Delete from Employees table
                # delete_employee_query = "DELETE FROM Employees WHERE employee_id = ?"
                # cursor.execute(delete_employee_query, (employee_id,))

                # Commit the transaction
                conn.commit()

                return {"status": "Success", "message": f"Employee ID '{employee_id}' deleted successfully."}
                
            except odbc.Error as e:
                conn.rollback()
                return {"status": "Failure", "message": f"Error deleting employee: {str(e)}"}
            finally:
                cursor.close()
                conn.autocommit = True
