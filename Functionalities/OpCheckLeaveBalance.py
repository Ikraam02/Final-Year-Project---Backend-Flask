import pypyodbc as odbc  # Import pypyodbc for database operations

class OpCheckLeaveBalance:
    def __init__(self, db_connection):
        self.db_connection = db_connection  # Store the database connection

    def get_leave_balance(self, data):

        employee_id = data.get('employee_id')
        
        if not employee_id:
            return {"status": "Failure", "message": "Employee ID is required."}

        try:
            cursor = self.db_connection.cursor()

            # Query to retrieve leave balance for the specified employee, including unpaid_leave
            query = """
                SELECT 
                    leave_balance_id, employee_id, 
                    annual_leave_entitlement, annual_leave_taken, 
                    sick_leave_entitlement, sick_leave_taken, 
                    casual_leave_entitlement, casual_leave_taken,
                    unpaid_leave
                FROM LeaveBalance
                WHERE employee_id = ?
            """
            cursor.execute(query, (employee_id,))
            result = cursor.fetchone()

            # Check if the query returned any results
            if result:
                # Map the result to a dictionary
                leave_balance_details = {
                    "leave_balance_id": result[0],
                    "employee_id": result[1],
                    "annual_leave_entitlement": result[2],
                    "annual_leave_taken": result[3],
                    "sick_leave_entitlement": result[4],
                    "sick_leave_taken": result[5],
                    "casual_leave_entitlement": result[6],
                    "casual_leave_taken": result[7],
                    "unpaid_leave": result[8]  # Adding unpaid_leave
                }
                
                return {"status": "Success", "data": leave_balance_details}
            else:
                return {"status": "Failure", "message": "No leave balance found for the provided employee ID."}

        except odbc.Error as e:
            return {"status": "Failure", "message": f"Error retrieving leave balance: {str(e)}"}
        finally:
            cursor.close()  # Close the cursor

    def add_leave_balance(self, data):

        required_fields = ['employee_id', 'annual_leave_entitlement', 'annual_leave_taken', 
                           'sick_leave_entitlement', 'sick_leave_taken', 
                           'casual_leave_entitlement', 'casual_leave_taken']
        
        # Check for missing fields
        for field in required_fields:
            if field not in data:
                return {"status": "Failure", "message": f"Missing required field: {field}"}

        try:
            cursor = self.db_connection.cursor()

            # Query to insert a new leave balance record, setting unpaid_leave to 0
            insert_query = """
                INSERT INTO LeaveBalance 
                (employee_id, annual_leave_entitlement, annual_leave_taken, 
                 sick_leave_entitlement, sick_leave_taken, 
                 casual_leave_entitlement, casual_leave_taken, unpaid_leave)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0)  -- Set unpaid_leave to 0
            """
            cursor.execute(insert_query, (
                data['employee_id'],
                data['annual_leave_entitlement'],
                data['annual_leave_taken'],
                data['sick_leave_entitlement'],
                data['sick_leave_taken'],
                data['casual_leave_entitlement'],
                data['casual_leave_taken']
            ))
            self.db_connection.commit()  # Commit the transaction

            return {"status": "Success", "message": "Leave balance added successfully."}

        except odbc.Error as e:
            self.db_connection.rollback()  # Roll back any changes if an error occurs
            return {"status": "Failure", "message": f"Error adding leave balance: {str(e)}"}
        finally:
            cursor.close()  # Close the cursor

    def delete_leave_balance(self, data):
        employee_id = data.get('employee_id')

        if not employee_id:
            return {"status": "Failure", "message": "Employee ID is required."}

        try:
            cursor = self.db_connection.cursor()

            # Query to delete leave balance for the specified employee
            delete_query = """
                DELETE FROM LeaveBalance
                WHERE employee_id = ?
            """
            cursor.execute(delete_query, (employee_id,))
            self.db_connection.commit()  # Commit the transaction

            if cursor.rowcount > 0:
                return {"status": "Success", "message": "Leave balance deleted successfully."}
            else:
                return {"status": "Failure", "message": "No leave balance found for the provided employee ID."}

        except odbc.Error as e:
            self.db_connection.rollback()  # Roll back any changes if an error occurs
            return {"status": "Failure", "message": f"Error deleting leave balance: {str(e)}"}
        finally:
            cursor.close()  # Close the cursor


    def get_all_employees_with_no_leave_balance(self):
        try:
            cursor = self.db_connection.cursor()

            # Query to get all employees who do not have any leave balance
            query = """
                SELECT 
                    u.username, u.email, e.employee_id, e.first_name, e.last_name, 
                    e.address, e.phone_number
                FROM Employees e
                LEFT JOIN LeaveBalance lb ON e.employee_id = lb.employee_id
                INNER JOIN Users u ON e.employee_id = u.employee_id
                WHERE lb.employee_id IS NULL
            """
            cursor.execute(query)
            results = cursor.fetchall()

            # Check if there are any results
            if results:
                employees_without_leave_balance = []
                
                for row in results:
                    employee_details = {
                        "username": row[0],
                        "email": row[1],
                        "employee_id": row[2],
                        "first_name": row[3],
                        "last_name": row[4],
                        "address": row[5],
                        "phone_number": row[6]
                    }
                    employees_without_leave_balance.append(employee_details)

                return {"status": "Success", "data": employees_without_leave_balance}
            else:
                return {"status": "Failure", "message": "No employees found without leave balance."}

        except odbc.Error as e:
            return {"status": "Failure", "message": f"Error retrieving employees: {str(e)}"}
        finally:
            cursor.close()

    def get_employees_with_leave_balance(self):
        try:
            cursor = self.db_connection.cursor()

            query = """
            SELECT e.employee_id, u.username, lb.annual_leave_entitlement, lb.annual_leave_taken, 
                lb.sick_leave_entitlement, lb.sick_leave_taken, lb.casual_leave_entitlement, lb.casual_leave_taken, lb.unpaid_leave
            FROM Employees e
            JOIN Users u ON e.employee_id = u.employee_id
            JOIN LeaveBalance lb ON e.employee_id = lb.employee_id
            WHERE lb.annual_leave_entitlement > 0 
            OR lb.sick_leave_entitlement > 0 
            OR lb.casual_leave_entitlement > 0
            """
            
            # Assuming you have a function to execute the query and return results
            cursor.execute(query)
            results = cursor.fetchall()
            
            employee_list = []
            for row in results:
                employee_data = {
                    "employee_id": row['employee_id'],
                    "username": row['username'],
                    "annual_leave": row['annual_leave_entitlement'],
                    "annual_taken": row['annual_leave_taken'],
                    "sick_leave": row['sick_leave_entitlement'],
                    "sick_taken": row['sick_leave_taken'],
                    "casual_leave": row['casual_leave_entitlement'],
                    "casual_taken": row['casual_leave_taken'],
                    "unpaid_leave": row['unpaid_leave']
                }
                employee_list.append(employee_data)
            
            return {"status": "Success", "data": employee_list}
        except odbc.Error as e:
            return {"status": "Failure", "message": f"Error retrieving employees: {str(e)}"}
        finally:
            cursor.close()

