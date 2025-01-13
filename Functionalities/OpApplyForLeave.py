import pypyodbc as odbc
from datetime import datetime

class OpApplyLeave:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def calculate_leave_duration(self, start_date, end_date):
        """Calculates the duration of the leave in days."""
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        return (end - start).days + 1

    def check_leave_balance(self, employee_id, leave_type, leave_duration):
        """Checks if the employee has sufficient leave balance for the given leave type."""
        try:
            cursor = self.db_connection.cursor()
            select_query = """
                SELECT annual_leave_entitlement, annual_leave_taken, 
                       sick_leave_entitlement, sick_leave_taken,
                       casual_leave_entitlement, casual_leave_taken
                FROM LeaveBalance
                WHERE employee_id = ?
            """
            cursor.execute(select_query, (employee_id,))
            leave_balance = cursor.fetchone()

            if not leave_balance:
                return {"status": "Failure", "message": "Leave balance not found for the employee."}

            # Check leave type and calculate leave balance
            if "annual" in leave_type.lower():
                entitlement = leave_balance[0]
                taken = leave_balance[1]
            elif "sick" in leave_type.lower():
                entitlement = leave_balance[2]
                taken = leave_balance[3]
            elif "casual" in leave_type.lower():
                entitlement = leave_balance[4]
                taken = leave_balance[5]
            elif "unpaid" in leave_type.lower():
                return {"status": "Success", "message": "Unpaid will be considered as absent."}
            else:
                return {"status": "Failure", "message": "Invalid leave type."}

            if taken + leave_duration > entitlement:
                return {"status": "Failure", "message": "Insufficient leave balance."}

            return {"status": "Success", "message": "Sufficient leave balance."}

        except odbc.Error as e:
            return {"status": "Failure", "message": f"Error checking leave balance: {str(e)}"}

        finally:
            cursor.close()

    def apply_leave(self, data):
        """Applies for leave based on the JSON request data."""
        try:
            cursor = self.db_connection.cursor()

            employee_id = data.get('employee_id')
            leave_type = data.get('leave_type')  # Now taking 'leave_type' directly
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            status = "Pending"
            reason = data.get('reason')
            application_date = data.get('application_date')

            # Validate required fields
            if not all([employee_id, leave_type, start_date, end_date, reason, application_date]):
                return {"status": "Failure", "message": "Missing required fields in request."}

            # Calculate the duration of the leave
            leave_duration = self.calculate_leave_duration(start_date, end_date)

            # Check if the employee has sufficient leave balance
            balance_check = self.check_leave_balance(employee_id, leave_type, leave_duration)

            if balance_check["status"] == "Failure":
                return balance_check  # Return the failure message if insufficient balance

            # Insert the leave application into the LeaveApplications table
            insert_query = """
                INSERT INTO LeaveApplications (employee_id, leave_type, start_date, end_date, status, reason, application_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(insert_query, (
                employee_id, leave_type, start_date, end_date, status, reason, application_date
            ))
            self.db_connection.commit()

            return {"status": "Success", "message": "Leave application submitted successfully and set to Pending."}

        except odbc.Error as e:
            self.db_connection.rollback()
            return {"status": "Failure", "message": f"Error applying leave: {str(e)}"}

        finally:
            cursor.close()

    def get_leave_applications(self, employee_id):
        cursor = self.db_connection.cursor()

        # Fetch pending leaves
        cursor.execute('''SELECT leave_application_id, start_date, end_date, reason, application_date, leave_type 
                        FROM LeaveApplications 
                        WHERE employee_id = ? AND status = 'Pending' ''', (employee_id,))
        pending_leaves = cursor.fetchall()

        # Fetch approved leaves
        cursor.execute('''SELECT leave_application_id, start_date, end_date, reason, application_date, approval_date, approved_by, leave_type 
                        FROM LeaveApplications 
                        WHERE employee_id = ? AND status = 'Approved' ''', (employee_id,))
        approved_leaves = cursor.fetchall()

        # Fetch rejected leaves
        cursor.execute('''SELECT leave_application_id, start_date, end_date, reason, application_date, rejected_by, rejection_reason, rejection_date, leave_type 
                        FROM LeaveApplications 
                        WHERE employee_id = ? AND status = 'Rejected' ''', (employee_id,))
        rejected_leaves = cursor.fetchall()

        # Ensure the correct mapping of fields
        pending_columns = ['leave_application_id', 'start_date', 'end_date', 'reason', 'application_date', 'leave_type']
        approved_columns = ['leave_application_id', 'start_date', 'end_date', 'reason', 'application_date', 'approval_date', 'approved_by', 'leave_type']
        rejected_columns = ['leave_application_id', 'start_date', 'end_date', 'reason', 'application_date', 'rejected_by', 'rejection_reason', 'rejection_date', 'leave_type']

        # Map each result to a dictionary with the correct column names
        return {
            'status': 'Success',
            'data': {
                'pending': [dict(zip(pending_columns, row)) for row in pending_leaves],
                'approved': [dict(zip(approved_columns, row)) for row in approved_leaves],
                'rejected': [dict(zip(rejected_columns, row)) for row in rejected_leaves]
            }
        }

    def get_all_pending_leave_applications(self):
            cursor = self.db_connection.cursor()

            # Query to fetch all pending leave applications
            cursor.execute('''SELECT leave_application_id, start_date, end_date, reason, application_date, leave_type, employee_id
                            FROM LeaveApplications
                            WHERE status = 'Pending' ''')
            pending_leaves = cursor.fetchall()

            # Define the column names for the pending leaves
            pending_columns = ['leave_application_id', 'start_date', 'end_date', 'reason', 'application_date', 'leave_type', 'employee_id']

            # Return pending leaves as a list of dictionaries
            return {
                'status': 'Success',
                'data': [dict(zip(pending_columns, row)) for row in pending_leaves]
         }

