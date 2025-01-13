import pypyodbc as odbc

class OpTrackLeaveHistory:
    def __init__(self, db_connection):
        self.db_connection = db_connection  # Store the database connection

    def get_leave_applications_by_employee(self, data):
        """Retrieve leave applications for a specific employee by extracting employee_id from data."""
        employee_id = data.get('employee_id')  # Extract employee_id from the data dictionary
        
        if not employee_id:
            return {"status": "Failure", "message": "Employee ID is required."}

        try:
            cursor = self.db_connection.cursor()

            # Query to get leave applications by employee_id
            query = """
                SELECT leave_application_id, start_date, end_date, status, reason, 
                       application_date, approval_date, approved_by, rejected_by, 
                       rejection_reason, rejection_date
                FROM LeaveApplications
                WHERE employee_id = ?
            """
            cursor.execute(query, (employee_id,))
            results = cursor.fetchall()

            if results:
                leave_applications = []
                for result in results:
                    leave_applications.append({
                        "leave_application_id": result[0],
                        "start_date": result[1],
                        "end_date": result[2],
                        "status": result[3],
                        "reason": result[4],
                        "application_date": result[5],
                        "approval_date": result[6],
                        "approved_by": result[7],
                        "rejected_by": result[8],
                        "rejection_reason": result[9],
                        "rejection_date": result[10]
                    })

                return {"status": "Success", "data": leave_applications}
            else:
                return {"status": "Failure", "message": "No leave applications found for the provided Employee ID."}

        except odbc.Error as e:
            return {"status": "Failure", "message": f"Error retrieving leave applications: {str(e)}"}

        finally:
            cursor.close()  # Close the cursor
