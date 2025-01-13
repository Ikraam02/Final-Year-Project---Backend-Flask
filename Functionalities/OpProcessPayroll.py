from datetime import datetime, timedelta
import pypyodbc as odbc
from Functionalities.OpGenerateAttendanceRep import OpGenerateAttendanceReport

class OpManagePayroll:
    def __init__(self, db_connection):
        self.db_connection = db_connection
        self.attendance_report = OpGenerateAttendanceReport(db_connection, public_holidays=['2024-10-31', '2024-12-25'])

    def add_payroll_record(self, data):
        try:
            cursor = self.db_connection.cursor()

            employee_id = data.get('employee_id')
            tax_rate = data.get('tax_rate', 0)  # Default to 0 if not provided
            bonus = data.get('bonus', 0)
            health_insurance = data.get('health_insurance', 0)
            retirement_contribution = data.get('retirement_contribution', 0)
            other_deductions = data.get('other_deductions', 0)

            # Check if tax_rate is valid
            if tax_rate is None:
                return {"status": "Failure", "message": "Tax rate is missing or invalid."}

            # Retrieve the current year dynamically
            current_year = datetime.now().year

            # Get the provided month from frontend
            provided_month = data.get('month')

            # Calculate the last day of the provided month in the current year
            last_day_of_month = self.get_last_day_of_month(current_year, provided_month)

            # Use the last day of the month as the payroll_date
            payroll_date = last_day_of_month.strftime('%Y-%m-%d')

            # Retrieve the base salary from Roles table
            base_salary_query = """
                SELECT r.salary
                FROM Roles r
                JOIN Users u ON r.role_id = u.role_id
                WHERE u.employee_id = ?
            """
            cursor.execute(base_salary_query, (employee_id,))
            base_salary_result = cursor.fetchone()
            if not base_salary_result:
                return {"status": "Failure", "message": "Base salary not found for this employee."}

            base_salary = base_salary_result[0]

            # Calculate the total number of days in the month
            total_days_in_month = self.calculate_days_in_month(current_year, provided_month)

            # Calculate unpaid_leave_deduction_per_day as base_salary / total_days_in_month
            unpaid_leave_deduction_per_day = base_salary / total_days_in_month

            # Retrieve the days_absent from the attendance report
            attendance_report = self.attendance_report.calculate_days_present_absent(employee_id, current_year, provided_month)
            if attendance_report["status"] == "Failure":
                return attendance_report

            days_absent = attendance_report["days_absent"]

            # Calculate unpaid leave deduction
            unpaid_leave_deduction = days_absent * unpaid_leave_deduction_per_day

            # Check if payroll record already exists for this employee and month
            check_query = """
                SELECT payroll_id
                FROM Payrolls
                WHERE employee_id = ? AND YEAR(payroll_date) = ? AND MONTH(payroll_date) = ?
            """
            cursor.execute(check_query, (employee_id, current_year, provided_month))
            existing_record = cursor.fetchone()

            if existing_record:
                return {"status": "Failure", "message": "Payroll record already exists for this employee and month."}

            # Calculate net salary
            payroll_data = self.calculate_net_salary(
                base_salary, bonus, health_insurance, retirement_contribution, unpaid_leave_deduction,
                tax_rate, other_deductions
            )

            # Insert payroll record into the table
            insert_query = """
                INSERT INTO Payrolls (employee_id, base_salary, bonus, deductions, tax, net_salary, payroll_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(insert_query, (
                employee_id,
                base_salary,
                bonus,
                payroll_data["deductions"],
                payroll_data["tax"],
                payroll_data["net_salary"],
                payroll_date
            ))
            self.db_connection.commit()

            return {"status": "Success", "message": "Payroll record added successfully."}

        except odbc.Error as e:
            return {"status": "Failure", "message": f"Error adding payroll record: {str(e)}"}

        finally:
            cursor.close()


    def get_last_day_of_month(self, year, month):
        try:
            month = int(month)
        except ValueError:
            raise ValueError("Invalid month format. Please enter a numeric month.")

        return self.calculate_last_day_of_month(year, month)

    def calculate_last_day_of_month(self, year, month):
        """Calculate the last day of the given month."""
        next_month = month % 12 + 1
        next_month_year = year + (month // 12)
        first_day_next_month = datetime(next_month_year, next_month, 1)
        last_day_of_month = first_day_next_month - timedelta(days=1)
        return last_day_of_month  # This is the datetime object

    def calculate_days_in_month(self, year, month):
        """Calculate the total number of days in the given month."""
        next_month = month % 12 + 1
        next_month_year = year + (month // 12)
        first_day_next_month = datetime(next_month_year, next_month, 1)
        last_day_of_month = first_day_next_month - timedelta(days=1)
        return last_day_of_month.day


    def calculate_net_salary(self, base_salary, bonus, health_insurance, retirement_contribution, unpaid_leave_deduction, tax_rate, other_deductions):
        """Calculate the net salary by deducting taxes and other deductions."""
        gross_salary = base_salary + bonus
        total_deductions = health_insurance + retirement_contribution + unpaid_leave_deduction + other_deductions
        tax = gross_salary * tax_rate
        net_salary = gross_salary - total_deductions - tax

        return {
            "deductions": total_deductions,
            "tax": tax,
            "net_salary": net_salary
        }


    def generate_monthly_report(self, data):
        try:
            cursor = self.db_connection.cursor()
            # Extract mandatory fields from JSON data
            employee_id = data.get('employee_id')
            year = data.get('year')
            month = data.get('month')
            if not all([employee_id, year, month]):
                return {"status": "Failure", "message": "Missing required fields: employee_id, year, or month."}

            # Fetch payroll records for the given employee in the specified month
            payroll_query = """
                SELECT payroll_id, base_salary, bonus, deductions, tax, net_salary, payroll_date
                FROM Payrolls
                WHERE employee_id = ? AND YEAR(payroll_date) = ? AND MONTH(payroll_date) = ?
            """
            cursor.execute(payroll_query, (employee_id, year, month))
            payroll_records = cursor.fetchall()

            # Prepare the report
            report = []
            for record in payroll_records:
                payroll_id, base_salary, bonus, deductions, tax, net_salary, payroll_date = record

                # Convert payroll_date to a datetime object if it is a string
                if isinstance(payroll_date, str):
                    payroll_date = datetime.strptime(payroll_date, '%Y-%m-%d')

                report.append({
                    "payroll_id": payroll_id,
                    "base_salary": base_salary,
                    "bonus": bonus,
                    "deductions": deductions,
                    "tax": tax,
                    "net_salary": net_salary,
                    "payroll_date": payroll_date.strftime('%Y-%m-%d')
                })

            return {"status": "Success", "report": report}

        except odbc.Error as e:
            return {"status": "Failure", "message": f"Error generating payroll report: {str(e)}"}

        finally:
            cursor.close()

    def OpGetUnprocessedPayrollEmployees(self):
        try:
            current_month = datetime.now().month
            current_year = datetime.now().year

            cursor = self.db_connection.cursor()

            # Subquery to get employee_ids who have processed payrolls this month
            subquery = """
                SELECT employee_id 
                FROM Payrolls 
                WHERE YEAR(payroll_date) = ? AND MONTH(payroll_date) = ?
            """

            cursor.execute(subquery, (current_year, current_month))
            processed_employee_ids = [row[0] for row in cursor.fetchall()]

            # Check if there are any processed employees
            if processed_employee_ids:
                # If processed_employee_ids is not empty, use the IN clause
                employee_query = """
                    SELECT e.employee_id, u.username, u.email, u.last_login
                    FROM Employees e
                    JOIN Users u ON e.employee_id = u.employee_id
                    WHERE e.employee_id NOT IN ({})
                """.format(','.join(['?']*len(processed_employee_ids)))

                cursor.execute(employee_query, processed_employee_ids)
            else:
                # If processed_employee_ids is empty, get all employees
                employee_query = """
                    SELECT e.employee_id, u.username, u.email, u.last_login
                    FROM Employees e
                    JOIN Users u ON e.employee_id = u.employee_id
                """
                cursor.execute(employee_query)

            employees = cursor.fetchall()

            result = []
            for employee in employees:
                result.append({
                    "employee_id": employee[0],
                    "username": employee[1],
                    "email": employee[2],
                    "last_login": employee[3]
                })

            return {"status": "Success", "data": result}

        except odbc.Error as e:
            return {"status": "Failure", "message": f"Error occurred: {str(e)}"}
        finally:
            cursor.close()


    def OpGetProcessedPayrollEmployees(self):
        try:
            current_month = datetime.now().month
            print("CUrrent",current_month)
            current_year = datetime.now().year

            cursor = self.db_connection.cursor()

            # Get employees whose payroll has been processed
            employee_query = """
                SELECT e.employee_id, u.username, u.email, u.last_login
                FROM Employees e
                JOIN Users u ON e.employee_id = u.employee_id
                JOIN Payrolls p ON e.employee_id = p.employee_id
                WHERE YEAR(p.payroll_date) = ? AND MONTH(p.payroll_date) = ?
            """

            cursor.execute(employee_query, (current_year, current_month))
            employees = cursor.fetchall()

            result = []
            for employee in employees:
                result.append({
                    "employee_id": employee[0],
                    "username": employee[1],
                    "email": employee[2],
                    "last_login": employee[3]
                })

            return {"status": "Success", "data": result}

        except odbc.Error as e:
            return {"status": "Failure", "message": f"Error occurred: {str(e)}"}
        finally:
            cursor.close()
