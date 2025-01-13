import pypyodbc as odbc
import json
from datetime import datetime, timedelta

class OpEmployeeDashboard:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def employee_dashboard(self, employee_id):
        try:
            cursor = self.db_connection.cursor()

            # First, get the department and role of the logged-in user based on employee_id
            department_role_query = """
                SELECT r.description, r.role_name, r.salary
                FROM Users u
                JOIN Roles r ON u.role_id = r.role_id
                WHERE u.employee_id = ?
            """
            cursor.execute(department_role_query, [employee_id])
            user_info = cursor.fetchone()

            if not user_info:
                return {"status": "Failure", "message": "Department or role not found for the user."}

            user_department = user_info[0]  # Department (description)
            user_role_name = user_info[1]   # Role (role_name)
            user_role_salary = user_info[2]   

            # Query to get all users in the same department (including the logged-in user)
            query = """
                SELECT 
                    u.username, 
                    u.email, 
                    u.last_login, 
                    u.employee_id,
                    r.role_name, 
                    CAST(r.description AS NVARCHAR(MAX)) AS description, 
                    r.salary
                FROM Users u
                JOIN Roles r ON u.role_id = r.role_id
                WHERE CAST(r.description AS NVARCHAR(MAX)) = ?
            """
            cursor.execute(query, [user_department])
            results = cursor.fetchall()

            if results:
                users = []
                total_number_of_employees = 0
                for row in results:
                    user_details = {
                        "username": row[0],
                        "email": row[1],
                        "last_login": row[2],
                        "employee_id": row[3],
                        "role_name": row[4],
                        "description": row[5],  # Department description
                        "salary": row[6]        # Salary
                    }
                    users.append(user_details)
                    total_number_of_employees += 1

                # Count pending leaves
                cursor.execute('''SELECT COUNT(*) 
                                FROM LeaveApplications 
                                WHERE employee_id = ? AND status = 'Pending' ''', (employee_id,))
                pending_leave_count = cursor.fetchone()[0]  # Fetch the count

                # Return the list of users, total number of employees, and the department
                return {
                    "status": "Success",
                    "job_title": user_role_name,
                    "base_salary": user_role_salary,
                    "total_number_of_employees": total_number_of_employees,
                    "department": user_department, # Return the department description
                    'pending_leave_count': pending_leave_count
                }
            else:
                return {"status": "Failure", "message": "No users found in the same department."}

        except odbc.Error as e:
            return {"status": "Failure", "message": f"Error retrieving department employees: {str(e)}"}
        finally:
            cursor.close()
