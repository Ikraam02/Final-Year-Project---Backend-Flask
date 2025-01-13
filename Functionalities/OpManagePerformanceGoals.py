import pypyodbc as odbc

class OpManagePerformanceGoals:
    def __init__(self, db_connection):
        self.db_connection = db_connection  # Store the database connection

    def add_performance_goal(self, data):
        """Add a new performance goal to the PerformanceGoals table."""
        required_fields = ['employee_id', 'criteria_id', 'goal_description', 'target_date', 'status']

        # Check for missing fields
        for field in required_fields:
            if field not in data:
                return {"status": "Failure", "message": f"Missing required field: {field}"}

        try:
            cursor = self.db_connection.cursor()

            # Check if the employee_id exists in the Employees table
            check_employee_query = "SELECT COUNT(*) FROM Employees WHERE employee_id = ?"
            cursor.execute(check_employee_query, (data['employee_id'],))
            existing_employee_count = cursor.fetchone()[0]

            if existing_employee_count == 0:
                return {"status": "Failure", "message": f"Employee with ID '{data['employee_id']}' does not exist."}

            # Check if the criteria_id exists in the Criteria table
            check_criteria_query = "SELECT COUNT(*) FROM PerformanceCriteria WHERE criteria_id = ?"
            cursor.execute(check_criteria_query, (data['criteria_id'],))
            existing_criteria_count = cursor.fetchone()[0]

            if existing_criteria_count == 0:
                return {"status": "Failure", "message": f"Criteria with ID '{data['criteria_id']}' does not exist."}

            # Insert a new performance goal into the PerformanceGoals table
            insert_query = """
                INSERT INTO PerformanceGoals (employee_id, criteria_id, goal_description, target_date, status)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(insert_query, (
                data['employee_id'],
                data['criteria_id'],
                data['goal_description'],
                data['target_date'],
                data['status']
            ))
            self.db_connection.commit()  # Commit the transaction

            return {"status": "Success", "message": "Performance goal added successfully."}

        except odbc.Error as e:
            self.db_connection.rollback()  # Roll back any changes if an error occurs
            return {"status": "Failure", "message": f"Error adding performance goal: {str(e)}"}

        finally:
            cursor.close()  # Close the cursor

    def update_performance_goal(self, data):
        goal_id = data.get('goal_id')
        employee_id = data.get('employee_id')
        criteria_id = data.get('criteria_id')
        goal_description = data.get('goal_description')
        target_date = data.get('target_date')
        status = data.get('status')

        if not goal_id:
            return {"status": "Failure", "message": "Goal ID is required."}

        try:
            cursor = self.db_connection.cursor()

            # Dynamically build the SQL update query
            update_query = "UPDATE PerformanceGoals SET "
            update_fields = []
            update_values = []

            if employee_id:
                update_fields.append("employee_id = ?")
                update_values.append(employee_id)
            if criteria_id:
                update_fields.append("criteria_id = ?")
                update_values.append(criteria_id)
            if goal_description:
                update_fields.append("goal_description = ?")
                update_values.append(goal_description)
            if target_date:
                update_fields.append("target_date = ?")
                update_values.append(target_date)
            if status:
                update_fields.append("status = ?")
                update_values.append(status)

            update_query += ", ".join(update_fields)
            update_query += " WHERE goal_id = ?"
            update_values.append(goal_id)

            cursor.execute(update_query, tuple(update_values))
            self.db_connection.commit()  # Commit the transaction

            if cursor.rowcount > 0:
                return {"status": "Success", "message": "Performance goal updated successfully."}
            else:
                return {"status": "Failure", "message": "No performance goal found for the provided Goal ID."}

        except odbc.Error as e:
            self.db_connection.rollback()  # Roll back any changes if an error occurs
            return {"status": "Failure", "message": f"Error updating performance goal: {str(e)}"}

        finally:
            cursor.close()  # Close the cursor

    def delete_performance_goal(self, data):
        """Delete a performance goal from the PerformanceGoals table."""
        goal_id = data.get('goal_id')

        if not goal_id:
            return {"status": "Failure", "message": "Goal ID is required."}

        try:
            cursor = self.db_connection.cursor()

            # Delete the performance goal from the PerformanceGoals table
            delete_query = """
                DELETE FROM PerformanceGoals WHERE goal_id = ?
            """
            cursor.execute(delete_query, (goal_id,))
            self.db_connection.commit()  # Commit the transaction

            if cursor.rowcount > 0:
                return {"status": "Success", "message": "Performance goal deleted successfully."}
            else:
                return {"status": "Failure", "message": "No performance goal found for the provided Goal ID."}

        except odbc.Error as e:
            self.db_connection.rollback()  # Roll back any changes if an error occurs
            return {"status": "Failure", "message": f"Error deleting performance goal: {str(e)}"}

        finally:
            cursor.close()  # Close the cursor

    def get_performance_goal(self, data):
        """Retrieve details of a specific performance goal from the PerformanceGoals table."""
        goal_id = data.get('goal_id')

        if not goal_id:
            return {"status": "Failure", "message": "Goal ID is required."}

        try:
            cursor = self.db_connection.cursor()

            # Query to get the performance goal details
            query = """
                SELECT goal_id, employee_id, criteria_id, goal_description, target_date, status
                FROM PerformanceGoals
                WHERE goal_id = ?
            """
            cursor.execute(query, (goal_id,))
            result = cursor.fetchone()

            if result:
                goal_details = {
                    "goal_id": result[0],
                    "employee_id": result[1],
                    "criteria_id": result[2],
                    "goal_description": result[3],
                    "target_date": result[4],
                    "status": result[5]
                }
                return {"status": "Success", "data": goal_details}
            else:
                return {"status": "Failure", "message": "No performance goal found for the provided Goal ID."}

        except odbc.Error as e:
            return {"status": "Failure", "message": f"Error retrieving performance goal: {str(e)}"}

        finally:
            cursor.close()  # Close the cursor

    def get_all_performance_goals(self):
        """Retrieve all performance goals from the PerformanceGoals table."""
        try:
            cursor = self.db_connection.cursor()

            # Query to get all performance goals
            query = """
                SELECT goal_id, employee_id, criteria_id, goal_description, target_date, status
                FROM PerformanceGoals
            """
            cursor.execute(query)
            results = cursor.fetchall()

            goals = []
            for result in results:
                goals.append({
                    "goal_id": result[0],
                    "employee_id": result[1],
                    "criteria_id": result[2],
                    "goal_description": result[3],
                    "target_date": result[4],
                    "status": result[5]
                })

            return {"status": "Success", "data": goals}

        except odbc.Error as e:
            return {"status": "Failure", "message": f"Error retrieving performance goals: {str(e)}"}

        finally:
            cursor.close()  # Close the cursor
