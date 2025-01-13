import pypyodbc as odbc
from datetime import datetime, timedelta

class OpGenerateAttendanceReport:
    def __init__(self, db_connection, public_holidays):
        self.db_connection = db_connection
        self.public_holidays = public_holidays

    def is_weekend(self, date):
        """Check if the given date is a weekend (Saturday or Sunday)."""
        return date.weekday() >= 5

    def is_public_holiday(self, date):
        """Check if the given date is a public holiday."""
        return date.strftime('%Y-%m-%d') in self.public_holidays

    def calculate_total_work_days(self, year, month):
        """Calculate the total work days (excluding weekends and public holidays) in a given month."""
        total_days = 0
        for day in range(1, 32):
            try:
                current_date = datetime(year, month, day).date()
            except ValueError:
                break

            if not self.is_weekend(current_date) and not self.is_public_holiday(current_date):
                total_days += 1
        return total_days

    def generate_attendance_report(self, data):
        employee_id = data.get('employee_id')
        year = data.get('year')
        month = data.get('month')

        if not employee_id or not year or not month:
            return {"status": "Failure", "message": "Employee ID, year, and month are required."}

        try:
            cursor = self.db_connection.cursor()

            # Calculate total work days in the month
            total_work_days = self.calculate_total_work_days(year, month)

            # Fetch the employee's attendance for the given month (using the 'date' field)
            attendance_query = """
                SELECT date, clock_in_time, clock_out_time
                FROM Attendance
                WHERE employee_id = ? AND YEAR(date) = ? AND MONTH(date) = ?
            """
            cursor.execute(attendance_query, (employee_id, year, month))
            attendance_records = cursor.fetchall()

            days_present = 0
            days_absent = total_work_days
            late_clockins = 0
            early_clockouts = 0
            total_working_hours = 0
            overtime_hours = 0

            for record in attendance_records:
                date_str, clock_in, clock_out = record

                # Convert 'date' from string to datetime if needed
                if isinstance(date_str, str):
                    date = datetime.strptime(date_str, '%Y-%m-%d').date()  # Assuming the format is 'YYYY-MM-DD'
                else:
                    date = date_str  # If it's already a datetime.date object

                if clock_in is not None and clock_out is not None:
                    days_present += 1
                    days_absent -= 1  # Reduce the number of absent days
                    clock_in_time = clock_in.time()
                    clock_out_time = clock_out.time()
                    # Assuming work hours are 9 AM to 5 PM
                    work_start_time = datetime(year, month, date.day, 9, 0).time()
                    work_end_time = datetime(year, month, date.day, 17, 0).time()
                    # Check for late clock-ins
                    if clock_in_time > work_start_time:
                        late_clockins += 1
                    # Check for early clock-outs
                    if clock_out_time < work_end_time:
                        early_clockouts += 1
                    # Calculate the total working hours
                    work_duration = (clock_out - clock_in).seconds / 3600  # Convert seconds to hours
                    total_working_hours += work_duration
                    # Calculate overtime (if clocked out after 5 PM)
                    if clock_out_time > work_end_time:
                        overtime = (datetime.combine(date, clock_out_time) - datetime.combine(date, work_end_time)).seconds / 3600
                        overtime_hours += overtime
            # Calculate the attendance percentage
            attendance_percentage = (days_present / total_work_days) * 100

            report = {
                "employee_id": employee_id,
                "year": year,
                "month": month,
                "total_work_days": total_work_days,
                "days_present": days_present,
                "days_absent": days_absent,
                "late_clockins": late_clockins,
                "early_clockouts": early_clockouts,
                "total_working_hours": round(total_working_hours, 2),
                "overtime_hours": round(overtime_hours, 2),
                "attendance_percentage": round(attendance_percentage, 2)
            }

            return {"status": "Success", "report": report}

        except odbc.Error as e:
            return {"status": "Failure", "message": f"Error generating attendance report: {str(e)}"}

        finally:
            cursor.close()


    def calculate_days_present_absent(self, employee_id, year, month):
        """Calculate the number of days an employee was present and absent in a given month."""
        try:
            cursor = self.db_connection.cursor()

            # Calculate total work days in the month
            total_work_days = self.calculate_total_work_days(year, month)

            # Fetch the employee's attendance for the given month (using the 'date' field)
            attendance_query = """
                SELECT date
                FROM Attendance
                WHERE employee_id = ? AND YEAR(date) = ? AND MONTH(date) = ?
            """
            cursor.execute(attendance_query, (employee_id, year, month))
            attendance_records = cursor.fetchall()

            days_present = len(attendance_records)
            days_absent = total_work_days - days_present

            return {
                "status": "Success",
                "employee_id": employee_id,
                "year": year,
                "month": month,
                "days_present": days_present,
                "days_absent": days_absent
            }

        except odbc.Error as e:
            return {"status": "Failure", "message": f"Error calculating days present/absent: {str(e)}"}

        finally:
            cursor.close()
