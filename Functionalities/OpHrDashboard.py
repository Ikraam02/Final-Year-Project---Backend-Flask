import pypyodbc as odbc
import json
from datetime import datetime, timedelta

class OpHrDashboard:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def hr_dashboard(self):
        #1
        query = "SELECT COUNT(*) AS total_users FROM Users"
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            total_users = result[0] if result else 0
            cursor.close()
        #2
            today = datetime.now().date()
            query = """
                SELECT COUNT(DISTINCT employee_id) AS employees_on_leave
                FROM LeaveApplications
                WHERE status = 'Approved'
                AND start_date <= ?
                AND end_date >= ?
            """
            cursor = self.db_connection.cursor()
            cursor.execute(query, (today, today))
            result = cursor.fetchone()
            employees_on_leave = result[0] if result else 0
            cursor.close()
        #3
            first_day_current_month = today.replace(day=1)
            last_day_previous_month = first_day_current_month - timedelta(days=1)
            first_day_previous_month = last_day_previous_month.replace(day=1)
            
            query = """
                SELECT SUM(net_salary) AS total_net_salary
                FROM Payrolls
                WHERE payroll_date >= ? AND payroll_date <= ?
            """
            cursor = self.db_connection.cursor()
            cursor.execute(query, (first_day_previous_month, last_day_previous_month))
            result = cursor.fetchone()
            total_net_salary = round(result[0]) if result and result[0] else 0
            cursor.close()
        #4
            query = """
                SELECT COUNT(DISTINCT employee_id) AS total_clocked_in
                FROM Attendance
                WHERE date = ? AND clock_in_time IS NOT NULL
            """
            cursor = self.db_connection.cursor()
            cursor.execute(query, (today,))
            result = cursor.fetchone()
            total_clocked_in = result[0] if result else 0
            cursor.close()
        #5
            query_total_users = "SELECT COUNT(*) FROM Users"
        
            # Query to get the number of users in the Information Technology department
            query_it_department_users = """
                SELECT COUNT(*)
                FROM Users u
                JOIN Roles r ON u.role_id = r.role_id
                WHERE CAST(r.description AS VARCHAR(MAX)) = 'Information Technology'
            """
            # Query to get the number of users in the Quality Assurance department
            query_qa_department_users = """
                SELECT COUNT(*)
                FROM Users u
                JOIN Roles r ON u.role_id = r.role_id
                WHERE CAST(r.description AS VARCHAR(MAX)) = 'Quality Assurance'
            """

            # Query to get the number of users in the Human Resource department
            query_hr_department_users = """
                SELECT COUNT(*)
                FROM Users u
                JOIN Roles r ON u.role_id = r.role_id
                WHERE CAST(r.description AS VARCHAR(MAX)) = 'Human Resource'
            """
            cursor = self.db_connection.cursor()
            
            # Fetch total number of users
            cursor.execute(query_total_users)
            total_users_result = cursor.fetchone()
            total_users = total_users_result[0] if total_users_result else 0
            
            if total_users == 0:
                return {"status": "Failure", "message": "No users found in the database."}
            
            # Fetch the number of users in each department
            cursor.execute(query_it_department_users)
            it_department_users_result = cursor.fetchone()
            it_department_users = it_department_users_result[0] if it_department_users_result else 0

            cursor.execute(query_qa_department_users)
            qa_department_users_result = cursor.fetchone()
            qa_department_users = qa_department_users_result[0] if qa_department_users_result else 0

            cursor.execute(query_hr_department_users)
            hr_department_users_result = cursor.fetchone()
            hr_department_users = hr_department_users_result[0] if hr_department_users_result else 0
            
            cursor.close()

            # Calculate the percentages with decimal places
            it_percentage = (it_department_users / total_users) * 100
            qa_percentage = (qa_department_users / total_users) * 100
            hr_percentage = (hr_department_users / total_users) * 100
            
            # Adjust percentages to ensure they add up to 100
            total_percentage = it_percentage + qa_percentage + hr_percentage
            adjustment_factor = 100 / total_percentage
            
            it_percentage = round(it_percentage * adjustment_factor, 2)
            qa_percentage = round(qa_percentage * adjustment_factor, 2)
            hr_percentage = round(hr_percentage * adjustment_factor, 2)

            #6 NUmber of pending leaves
            cursor = self.db_connection.cursor()
            cursor.execute('''SELECT COUNT(*) FROM LeaveApplications WHERE status = 'Pending' ''')
            total_pending_leaves = cursor.fetchone()[0]


            #7 Return employees with no leave balance
            cursor = self.db_connection.cursor()
            # Query to count the total number of employees who do not have any leave balance
            query = """
                SELECT COUNT(*)
                FROM Employees e
                LEFT JOIN LeaveBalance lb ON e.employee_id = lb.employee_id
                INNER JOIN Users u ON e.employee_id = u.employee_id
                WHERE lb.employee_id IS NULL
            """
            cursor.execute(query)
            total_employees_no_leave_balance = cursor.fetchone()[0]  # Fetch the result which is a single number


            #8 Get Unprocessed payroll
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
                # If processed_employee_ids is not empty, use the IN clause and count employees
                employee_query = """
                    SELECT COUNT(*)
                    FROM Employees e
                    JOIN Users u ON e.employee_id = u.employee_id
                    WHERE e.employee_id NOT IN ({})
                """.format(','.join(['?']*len(processed_employee_ids)))

                cursor.execute(employee_query, processed_employee_ids)
            else:
                # If processed_employee_ids is empty, count all employees
                employee_query = """
                    SELECT COUNT(*)
                    FROM Employees e
                    JOIN Users u ON e.employee_id = u.employee_id
                """
                cursor.execute(employee_query)

            count = cursor.fetchone()[0]




        
            current_year = datetime.now().year

            cursor = self.db_connection.cursor()

            # Subquery to get employee_ids who have done their appraisal this year
            subquery = """
                SELECT employee_id 
                FROM Appraisals 
                WHERE YEAR(appraisal_date) = ?
            """
            cursor.execute(subquery, (current_year,))
            appraised_employee_ids = [row[0] for row in cursor.fetchall()]

            # Check if there are any employees who have completed appraisals
            if appraised_employee_ids:
                # Use the NOT IN clause to find employees who haven't done their appraisal
                employee_query = """
                    SELECT COUNT(*)
                    FROM Employees e
                    JOIN Users u ON e.employee_id = u.employee_id
                    WHERE e.employee_id NOT IN ({})
                """.format(','.join(['?'] * len(appraised_employee_ids)))

                cursor.execute(employee_query, appraised_employee_ids)
            else:
                # If no employee has done an appraisal, count all employees
                employee_query = """
                    SELECT COUNT(*)
                    FROM Employees e
                    JOIN Users u ON e.employee_id = u.employee_id
                """
                cursor.execute(employee_query)

            count = cursor.fetchone()[0]
         
            return {"status": "Success", "total_users": total_users, "employees_on_leave_today": employees_on_leave
                    , "total_net_salary_previous_month": total_net_salary,  "total_employees_clocked_in_today": total_clocked_in,
                "it_percentage": it_percentage,
                "qa_percentage": qa_percentage,
                "hr_percentage": hr_percentage,
                'total_pending_leaves': total_pending_leaves,
                "total_employees_with_no_leave_balance": total_employees_no_leave_balance,
                "unprocessed_payroll_count": count,
                "unappraised_employee_count": count}
        except odbc.Error as e:
            print("Database query error:", e)
            return {"status": "Failure", "message": "Error fetching total users."}
