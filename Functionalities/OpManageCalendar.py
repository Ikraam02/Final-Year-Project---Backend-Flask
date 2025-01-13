import pypyodbc as odbc
from datetime import datetime, timedelta

class OpCalendarManager:
    def __init__(self, db_connection):
        self.db_connection = db_connection  # Store the database connection
        self.public_holidays_2025 = [
            {'date': '2025-01-01', 'holiday_name': "New Year's Day"},  # New Year's Day
            {'date': '2025-05-01', 'holiday_name': "Labor Day"},       # Labor Day
            {'date': '2025-08-31', 'holiday_name': "National Day"},    # National Day
            {'date': '2025-12-25', 'holiday_name': "Christmas"}        # Christmas
        ]

    def get_day_type(self, date):
        """Determine the type of day: Weekday, Weekend, or Public Holiday."""
        for holiday in self.public_holidays_2025:
            if date.strftime('%Y-%m-%d') == holiday['date']:
                return 'Public Holiday', holiday['holiday_name']
        if date.weekday() >= 5:  # Saturday and Sunday
            return 'Weekend', None
        else:
            return 'Weekday', None

    def generate_calendar_data(self):
        """Generate the calendar for the year 2025 and store it in the database."""
        start_date = datetime(2025, 1, 2)  # Start from 2nd January 2025
        end_date = datetime(2025, 12, 31)  # Until 31st December 2025
        week_number = 1

        try:
            cursor = self.db_connection.cursor()
            current_date = start_date

            while current_date <= end_date:
                day_name = current_date.strftime('%A')
                type_of_day, holiday_name = self.get_day_type(current_date)

                # Insert the calendar data into the table, with optional holiday_name
                insert_query = """
                    INSERT INTO Calendar (week_number, date, day_name, type_of_day, holiday_name)
                    VALUES (?, ?, ?, ?, ?)
                """
                cursor.execute(insert_query, (
                    week_number,
                    current_date.strftime('%Y-%m-%d'),
                    day_name,
                    type_of_day,
                    holiday_name
                ))

                # Increment week number on each Monday
                if current_date.weekday() == 0 and current_date != start_date:
                    week_number += 1

                current_date += timedelta(days=1)

            self.db_connection.commit()
            print("Calendar data for 2025 inserted successfully.")

        except odbc.Error as e:
            self.db_connection.rollback()
            print(f"Error inserting calendar data: {str(e)}")

        finally:
            cursor.close()

    def update_public_holiday(self, data):
        """Update the type of day to 'Public Holiday' and set the holiday name for a given date."""
        try:
            cursor = self.db_connection.cursor()

            # Get the date and holiday name from the JSON request
            date_to_update = data.get('date')
            holiday_name = data.get('holiday_name')

            if not date_to_update or not holiday_name:
                return {"status": "Failure", "message": "Both date and holiday_name are required."}

            # Check if the date is in the correct format
            try:
                date_obj = datetime.strptime(date_to_update, '%Y-%m-%d')
            except ValueError:
                return {"status": "Failure", "message": "Invalid date format. Use 'YYYY-MM-DD'."}

            # Check if the date exists in the calendar
            select_query = """
                SELECT * FROM Calendar WHERE date = ?
            """
            cursor.execute(select_query, (date_to_update,))
            result = cursor.fetchone()

            if not result:
                return {"status": "Failure", "message": "Date not found in calendar."}

            # Update the type_of_day to 'Public Holiday' and store the holiday name
            update_query = """
                UPDATE Calendar 
                SET type_of_day = 'Public Holiday', holiday_name = ? 
                WHERE date = ?
            """
            cursor.execute(update_query, (holiday_name, date_to_update))
            self.db_connection.commit()

            return {"status": "Success", "message": f"Date {date_to_update} updated to Public Holiday: {holiday_name}."}

        except odbc.Error as e:
            self.db_connection.rollback()
            return {"status": "Failure", "message": f"Error updating public holiday: {str(e)}"}

        finally:
            cursor.close()
