import pypyodbc as odbc
from datetime import datetime
import calendar


class OpMonitorAttendance:
    def __init__(self, db_connection, public_holidays):
        self.db_connection = db_connection
        self.public_holidays = public_holidays

    def is_weekend(self, date):
        return date.weekday() >= 5

    def is_public_holiday(self, date):
        """Check if the given date is a public holiday."""
        return date.strftime('%Y-%m-%d') in self.public_holidays

    def generate_attendance_row(self, data):
        employee_id = data.get('employee_id')
        
        if not employee_id:
            return {"status": "Failure", "message": "Employee ID is required."}

        current_date = datetime.now().date()

        # Check if today is a weekend or public holiday
        if self.is_weekend(current_date):
            return {"status": "Failure", "message": "Attendance cannot be logged on weekends."}
        if self.is_public_holiday(current_date):
            return {"status": "Failure", "message": "Attendance cannot be logged on public holidays."}

        try:
            cursor = self.db_connection.cursor()

            # Check if the employee has already logged in today
            check_attendance_query = """
                SELECT COUNT(*) 
                FROM Attendance 
                WHERE employee_id = ? AND date = ?
            """
            cursor.execute(check_attendance_query, (employee_id, current_date))
            attendance_count = cursor.fetchone()[0]

            if attendance_count > 0:
                return {"status": "Failure", "message": "Attendance already logged for today."}

            # Check the last login time from the Users table
            check_last_login_query = """
                SELECT last_login 
                FROM Users 
                WHERE employee_id = ?
            """
            cursor.execute(check_last_login_query, (employee_id,))
            last_login_result = cursor.fetchone()

            if not last_login_result:
                return {"status": "Failure", "message": "Employee does not exist in the Users table."}

            last_login = last_login_result[0]

            # If last_login is None, allow attendance to be generated
            if last_login is not None:
                # Compare only the date part of last_login with the current date
                if last_login.date() == current_date:
                    return {"status": "Failure", "message": "Attendance already logged based on last login."}

            # Generate a new attendance row
            insert_attendance_query = """
                INSERT INTO Attendance (employee_id, clock_in_time, clock_out_time, date)
                VALUES (?, NULL, NULL, ?)
            """
            cursor.execute(insert_attendance_query, (employee_id, current_date))
            self.db_connection.commit()

            return {"status": "Success", "message": "Attendance row generated successfully. Please Clock-In"}

        except odbc.Error as e:
            self.db_connection.rollback()
            return {"status": "Failure", "message": f"Error generating attendance: {str(e)}"}

        finally:
            cursor.close()

    def clock_in(self, data):
        employee_id = data.get('employee_id')
        clock_in_time = data.get('clock_in_time')
        if not employee_id or not clock_in_time:
            return {"status": "Failure", "message": "Employee ID and clock-in time are required."}

        current_date = datetime.now().date()
        try:
            cursor = self.db_connection.cursor()

            # Check if there's an attendance row for today
            check_attendance_query = """
                SELECT clock_in_time
                FROM Attendance
                WHERE employee_id = ? AND date = ?
            """
            cursor.execute(check_attendance_query, (employee_id, current_date))
            result = cursor.fetchone()
            if result:
                # If a row exists but clock_in_time is already set, return a failure message
                if result[0] is not None:
                    return {"status": "Failure", "message": "Clock-in time is already set for today."}
            else:
                # If no attendance row exists, generate a new one
                insert_attendance_query = """
                    INSERT INTO Attendance (employee_id, clock_in_time, clock_out_time, date)
                    VALUES (?, ?, NULL, ?)
                """
                cursor.execute(insert_attendance_query, (employee_id, clock_in_time, current_date))
                self.db_connection.commit()

                return {"status": "Success", "message": "Attendance row created and clock-in time set successfully."}   
            # If attendance row exists but clock_in_time is not set, update it
            update_clock_in_query = """
                UPDATE Attendance
                SET clock_in_time = ?
                WHERE employee_id = ? AND date = ?
            """
            cursor.execute(update_clock_in_query, (clock_in_time, employee_id, current_date))
            self.db_connection.commit()

            if cursor.rowcount > 0:
                return {"status": "Success", "message": "Clock-in time updated successfully."}
            else:
                return {"status": "Failure", "message": "Failed to update clock-in time."}

        except odbc.Error as e:
            self.db_connection.rollback()
            return {"status": "Failure", "message": f"Error updating clock-in time: {str(e)}"}

        finally:
            cursor.close()


    def clock_out(self, data):
        employee_id = data.get('employee_id')
        clock_out_time_str = data.get('clock_out_time')
        cursor = self.db_connection.cursor()
        if not employee_id or not clock_out_time_str:
            return {"status": "Failure", "message": "Employee ID and clock-out time are required."}

        try:
            # Convert the clock_out_time to a datetime object using fromisoformat
            clock_out_time = datetime.fromisoformat(clock_out_time_str.replace('Z', '+00:00'))  # Replace 'Z' with UTC
            # Convert clock_out_time to offset-naive by stripping timezone info
            clock_out_time_naive = clock_out_time.replace(tzinfo=None)
            # Check if clock_in_time is set
            check_clock_in_query = """
                SELECT clock_in_time
                FROM Attendance
                WHERE employee_id = ? AND date = ?
            """
            cursor.execute(check_clock_in_query, (employee_id, datetime.now().date()))
            result = cursor.fetchone()
            if not result or result[0] is None:
                return {"status": "Failure", "message": "Cannot clock out before clocking in."}

            clock_in_time = result[0]
            # Ensure clock_out_time is after clock_in_time
            if clock_out_time_naive <= clock_in_time:
                return {"status": "Failure", "message": "Clock-out time must be after the clock-in time."}

            # Check if clock_out_time is already set
            check_clock_out_query = """
                SELECT clock_out_time
                FROM Attendance
                WHERE employee_id = ? AND date = ?
            """
            cursor.execute(check_clock_out_query, (employee_id, datetime.now().date()))
            result = cursor.fetchone()
            
            if result and result[0] is not None:
                return {"status": "Failure", "message": "Clock-out time is already set."}

            # Update clock_out_time for the attendance row
            update_query = """
                UPDATE Attendance
                SET clock_out_time = ?
                WHERE employee_id = ? AND date = ?
            """
            cursor.execute(update_query, (clock_out_time_naive, employee_id, datetime.now().date()))
            self.db_connection.commit()

            if cursor.rowcount > 0:
                return {"status": "Success", "message": "Clock-out time updated successfully."}
            else:
                return {"status": "Failure", "message": "No attendance row found for today."}

        except ValueError as ve:
            return {"status": "Failure", "message": f"Invalid clock-out time format: {str(ve)}"}
        except odbc.Error as e:
            self.db_connection.rollback()
            return {"status": "Failure", "message": f"Error updating clock-out time: {str(e)}"}
        finally:
            cursor.close()


    def get_monthly_attendance_by_data(self, data):
        """Retrieve all attendance records for a particular month based on the employee_id from the JSON data."""
        
        # Extracting values from the 'data' dictionary
        employee_id = data.get('employee_id')
        year = data.get('year')
        month = data.get('month')
        print(employee_id, " ", year, " ", month)
        
        # Validate the necessary inputs
        if not employee_id or not year or not month:
            return {"status": "Failure", "message": "Employee ID, year, and month are required."}

        try:
            # Convert year to integer
            year = int(year)
            
            # Convert month name to month number
            month_number = list(calendar.month_name).index(month)
            if month_number == 0:
                return {"status": "Failure", "message": "Invalid month name provided."}
            
            cursor = self.db_connection.cursor()

            # Define the start and end date for the specified month
            start_date = datetime(year, month_number, 1)
            if month_number == 12:  # Handle December's next month as January of next year
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month_number + 1, 1)

            # Query to get all attendance records for the employee for the specified month
            select_attendance_query = """
                SELECT attendance_id, employee_id, clock_in_time, clock_out_time, date
                FROM Attendance
                WHERE employee_id = ? AND date >= ? AND date < ?
                ORDER BY date ASC
            """
            cursor.execute(select_attendance_query, (employee_id, start_date, end_date))
            attendance_records = cursor.fetchall()
    
            if not attendance_records:
                return {"status": "Failure", "message": "No attendance records found for the specified month."}

            # Define the column names for the attendance records
            attendance_columns = ['attendance_id', 'employee_id', 'clock_in_time', 'clock_out_time', 'date']

            # Return attendance records as a list of dictionaries
            return {
                'status': 'Success',
                'data': [dict(zip(attendance_columns, record)) for record in attendance_records]
            }

        except odbc.Error as e:
            return {"status": "Failure", "message": f"Error retrieving attendance records: {str(e)}"}

        finally:
            cursor.close()

