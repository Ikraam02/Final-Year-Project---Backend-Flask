import pypyodbc as odbc  # Import pypyodbc for database operations

class OpGetAllUsers:
    def __init__(self, db_connection):
        self.db_connection = db_connection  # Store the database connection

    def get_users_in_same_department(self, employee_id):
        try:
            cursor = self.db_connection.cursor()

            # First, get the department and role of the logged-in user based on employee_id
            department_role_query = """
                SELECT r.description, r.role_name
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

            # Check if the user is a manager (checking if 'Manager' is part of the role name)
            is_manager = 'manager' in user_role_name.lower()

            # Query to get all users in the same department excluding the logged-in user
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
                WHERE CAST(r.description AS NVARCHAR(MAX)) = ? AND u.employee_id != ?
            """
            cursor.execute(query, [user_department, employee_id])
            results = cursor.fetchall()

            if results:
                users = []
                for row in results:
                    user_details = {
                        "username": row[0],
                        "email": row[1],
                        "last_login": row[2],
                        "employee_id": row[3],
                        "role_name": row[4],
                        "description": row[5],
                        "salary": row[6]
                    }
                    users.append(user_details)
                
                # Return the list of users, the department, and if the user is a manager
                return {
                    "status": "Success",
                    "data": users,
                    "isManager": is_manager,  # Return if the user is a manager (keyword match)
                    "department": user_department  # Return the user's department
                }
            else:
                return {"status": "Failure", "message": "No users found in the same department."}

        except odbc.Error as e:
            return {"status": "Failure", "message": f"Error retrieving users: {str(e)}"}
        finally:
            cursor.close()


    def get_all_users(self):
        try:
            cursor = self.db_connection.cursor()
            query = """
                SELECT 
                    u.username, 
                    u.email, 
                    u.last_login, 
                    u.employee_id,
                    r.role_name, 
                    r.description, 
                    r.salary
                FROM Users u
                JOIN Roles r ON u.role_id = r.role_id
            """
            cursor.execute(query)
            results = cursor.fetchall()

            # Check if the query returned any results
            if results:
                # Map the results to a list of dictionaries
                users = []
                for row in results:
                    user_details = {
                        "username": row[0],
                        "email": row[1],
                        "last_login": row[2],
                        "employee_id": row[3],
                        "role_name": row[4],
                        "description": row[5],
                        "salary": row[6]
                    }
                    users.append(user_details)
                return {"status": "Success", "data": users}
            else:
                return {"status": "Failure", "message": "No users found."}

        except odbc.Error as e:
            return {"status": "Failure", "message": f"Error retrieving users: {str(e)}"}
        finally:
            cursor.close()  # Close the cursor


    def get_all_users_for_attendance_report(self):
        try:
            cursor = self.db_connection.cursor()

            # Query to retrieve employee_id, username, email, and last_login
            query = """
                SELECT 
                    u.employee_id,
                    u.username, 
                    u.email, 
                    u.last_login
                FROM Users u
            """
            cursor.execute(query)
            results = cursor.fetchall()

            # Check if the query returned any results
            if results:
                # Map the results to a list of dictionaries
                users = []
                for row in results:
                    user_details = {
                        "employee_id": row[0],
                        "username": row[1],
                        "email": row[2],
                        "last_login": row[3],
                    }
                    users.append(user_details)
                return {"status": "Success", "data": users}
            else:
                return {"status": "Failure", "message": "No users found."}

        except odbc.Error as e:
            return {"status": "Failure", "message": f"Error retrieving users: {str(e)}"}
        finally:
            cursor.close()

