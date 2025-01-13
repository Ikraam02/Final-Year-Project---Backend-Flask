import pypyodbc as odbc
from datetime import datetime, timedelta

class OpApproveLeave:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def approve_leave(self, data):
        try:
            cursor = self.db_connection.cursor()

            # Get the required fields from the JSON request
            leave_application_id = data.get('leave_application_id')
            approved_by = data.get('approved_by')  # HR employee approving the leave
            approval_date = datetime.now().strftime('%Y-%m-%d')  # Set the current date as approval date

            if not leave_application_id or not approved_by:
                return {"status": "Failure", "message": "Missing required fields: leave_application_id or approved_by."}

            # Fetch the leave application details
            select_application_query = """
                SELECT employee_id, leave_type, start_date, end_date, status FROM LeaveApplications WHERE leave_application_id = ?
            """
            cursor.execute(select_application_query, (leave_application_id,))
            leave_application = cursor.fetchone()

            if not leave_application:
                return {"status": "Failure", "message": "Leave application not found."}

            employee_id, leave_type, start_date, end_date, status = leave_application

            if status.lower() != 'pending':
                return {"status": "Failure", "message": "Only pending leave applications can be approved."}

            # Calculate leave duration
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            leave_duration = (end - start).days + 1

            # Fetch the leave balance for the employee
            select_balance_query = """
                SELECT annual_leave_entitlement, annual_leave_taken, 
                    sick_leave_entitlement, sick_leave_taken, 
                    casual_leave_entitlement, casual_leave_taken, unpaid_leave 
                FROM LeaveBalance WHERE employee_id = ?
            """
            cursor.execute(select_balance_query, (employee_id,))
            leave_balance = cursor.fetchone()

            if not leave_balance:
                return {"status": "Failure", "message": "Leave balance not found for the employee."}

            # Determine leave type and update the corresponding balance
            leave_type = leave_type.lower()

            if leave_type == "annual":
                entitlement, taken = leave_balance[0], leave_balance[1]
                new_taken = taken + leave_duration
                update_balance_query = """
                    UPDATE LeaveBalance SET annual_leave_taken = ? WHERE employee_id = ?
                """
            elif leave_type == "sick":
                entitlement, taken = leave_balance[2], leave_balance[3]
                new_taken = taken + leave_duration
                update_balance_query = """
                    UPDATE LeaveBalance SET sick_leave_taken = ? WHERE employee_id = ?
                """
            elif leave_type == "casual":
                entitlement, taken = leave_balance[4], leave_balance[5]
                new_taken = taken + leave_duration
                update_balance_query = """
                    UPDATE LeaveBalance SET casual_leave_taken = ? WHERE employee_id = ?
                """
            elif leave_type == "unpaid":
                unpaid_leave = leave_balance[6]
                new_unpaid_leave = unpaid_leave + leave_duration
                update_balance_query = """
                    UPDATE LeaveBalance SET unpaid_leave = ? WHERE employee_id = ?
                """
                cursor.execute(update_balance_query, (new_unpaid_leave, employee_id))
            else:
                return {"status": "Failure", "message": "Unsupported leave type."}

            # Check if the leave balance exceeds entitlement (except for unpaid leave)
            if leave_type != "unpaid" and new_taken > entitlement:
                return {"status": "Failure", "message": "Leave application exceeds the leave entitlement."}

            # Update leave balance for the employee (for non-unpaid leave types)
            if leave_type != "unpaid":
                cursor.execute(update_balance_query, (new_taken, employee_id))

            # Update the leave application to set it as 'Approved'
            update_application_query = """
                UPDATE LeaveApplications
                SET status = 'Approved', approval_date = ?, approved_by = ?
                WHERE leave_application_id = ?
            """
            cursor.execute(update_application_query, (approval_date, approved_by, leave_application_id))

            self.db_connection.commit()

            # Generate attendance for leave days (only for paid leave)
            if leave_type != "unpaid":
                self.generate_leave_attendance(employee_id, start_date, end_date)

            return {"status": "Success", "message": f"Leave application {leave_application_id} approved successfully."}

        except odbc.Error as e:
            self.db_connection.rollback()
            return {"status": "Failure", "message": f"Error approving leave: {str(e)}"}

        finally:
            cursor.close()


    def generate_leave_attendance(self, employee_id, start_date, end_date):

        try:
            cursor = self.db_connection.cursor()

            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')

            leave_date = start
            while leave_date <= end:
                # Ensure the leave day is not a weekend or public holiday (this check can be extended as needed)
                if leave_date.weekday() < 5:  # Weekday check (0-4 are weekdays)
                    clock_in_time = datetime.combine(leave_date, datetime.strptime("09:00:00", "%H:%M:%S").time())
                    clock_out_time = datetime.combine(leave_date, datetime.strptime("18:00:00", "%H:%M:%S").time())

                    # Insert attendance row for the leave day
                    insert_attendance_query = """
                        INSERT INTO Attendance (employee_id, clock_in_time, clock_out_time, date)
                        VALUES (?, ?, ?, ?)
                    """
                    cursor.execute(insert_attendance_query, (employee_id, clock_in_time, clock_out_time, leave_date.strftime('%Y-%m-%d')))

                leave_date += timedelta(days=1)

            self.db_connection.commit()

        except odbc.Error as e:
            self.db_connection.rollback()
            return {"status": "Failure", "message": f"Error generating leave attendance: {str(e)}"}

        finally:
            cursor.close()
