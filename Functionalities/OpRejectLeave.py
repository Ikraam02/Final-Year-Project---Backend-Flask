import pypyodbc as odbc
from datetime import datetime

class OpRejectLeave:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def reject_leave(self, data):
        try:
            cursor = self.db_connection.cursor()

            # Get the required fields from the JSON request
            leave_application_id = data.get('leave_application_id')
            rejected_by = data.get('rejected_by')  # HR employee rejecting the leave
            rejection_reason = "Personal Reason"  # Optional rejection reason
            rejection_date = datetime.now().strftime('%Y-%m-%d')  # Set the current date as rejection date

            if not leave_application_id or not rejected_by:
                return {"status": "Failure", "message": "Missing required fields: leave_application_id or rejected_by."}

            # Fetch the leave application details
            select_application_query = """
                SELECT employee_id, status FROM LeaveApplications WHERE leave_application_id = ?
            """
            cursor.execute(select_application_query, (leave_application_id,))
            leave_application = cursor.fetchone()

            if not leave_application:
                return {"status": "Failure", "message": "Leave application not found."}

            employee_id, status = leave_application

            if status.lower() != 'pending':
                return {"status": "Failure", "message": "Only pending leave applications can be rejected."}

            # Update the leave application to set it as 'Rejected'
            update_application_query = """
                UPDATE LeaveApplications
                SET status = 'Rejected', rejection_reason = ?, rejection_date = ?, rejected_by = ?
                WHERE leave_application_id = ?
            """
            cursor.execute(update_application_query, (
                rejection_reason, rejection_date, rejected_by, leave_application_id
            ))

            self.db_connection.commit()

            return {"status": "Success", "message": f"Leave application {leave_application_id} rejected successfully."}

        except odbc.Error as e:
            self.db_connection.rollback()
            return {"status": "Failure", "message": f"Error rejecting leave: {str(e)}"}

        finally:
            cursor.close()

