import pypyodbc as odbc

class OpManageLeaveTypes:
    def __init__(self, db_connection):
        self.db_connection = db_connection  # Store the database connection

    def add_leave_type(self, data):
        """Add a new leave type to the LeaveTypes table, ensuring the leave_type_name is unique."""
        required_fields = ['leave_type_name', 'description']

        # Check for missing fields
        for field in required_fields:
            if field not in data:
                return {"status": "Failure", "message": f"Missing required field: {field}"}

        try:
            cursor = self.db_connection.cursor()

            # Check if the leave_type_name already exists
            check_query = "SELECT COUNT(*) FROM LeaveTypes WHERE leave_type_name = ?"
            cursor.execute(check_query, (data['leave_type_name'],))
            existing_leave_type_count = cursor.fetchone()[0]

            if existing_leave_type_count > 0:
                return {"status": "Failure", "message": f"Leave type with name '{data['leave_type_name']}' already exists."}

            # Insert a new leave type into the LeaveTypes table
            insert_query = """
                INSERT INTO LeaveTypes (leave_type_name, description)
                VALUES (?, ?)
            """
            cursor.execute(insert_query, (
                data['leave_type_name'],
                data['description']
            ))
            self.db_connection.commit()  # Commit the transaction

            return {"status": "Success", "message": "Leave type added successfully."}

        except odbc.Error as e:
            self.db_connection.rollback()  # Roll back any changes if an error occurs
            return {"status": "Failure", "message": f"Error adding leave type: {str(e)}"}

        finally:
            cursor.close()  # Close the cursor

    def update_leave_type(self, data):
        """Update an existing leave type in the LeaveTypes table."""
        leave_type_id = data.get('leave_type_id')
        leave_type_name = data.get('leave_type_name')
        description = data.get('description')

        if not leave_type_id:
            return {"status": "Failure", "message": "Leave type ID is required."}

        if not (leave_type_name or description):
            return {"status": "Failure", "message": "At least one field to update must be provided."}

        try:
            cursor = self.db_connection.cursor()

            # Dynamically build the SQL update query
            update_query = "UPDATE LeaveTypes SET "
            update_fields = []
            update_values = []

            if leave_type_name:
                update_fields.append("leave_type_name = ?")
                update_values.append(leave_type_name)
            if description:
                update_fields.append("description = ?")
                update_values.append(description)

            update_query += ", ".join(update_fields)
            update_query += " WHERE leave_type_id = ?"
            update_values.append(leave_type_id)

            cursor.execute(update_query, tuple(update_values))
            self.db_connection.commit()  # Commit the transaction

            if cursor.rowcount > 0:
                return {"status": "Success", "message": "Leave type updated successfully."}
            else:
                return {"status": "Failure", "message": "No leave type found for the provided Leave Type ID."}

        except odbc.Error as e:
            self.db_connection.rollback()  # Roll back any changes if an error occurs
            return {"status": "Failure", "message": f"Error updating leave type: {str(e)}"}

        finally:
            cursor.close()  # Close the cursor

    def delete_leave_type(self, data):
        """Delete a leave type from the LeaveTypes table."""
        leave_type_id = data.get('leave_type_id')

        if not leave_type_id:
            return {"status": "Failure", "message": "Leave type ID is required."}

        try:
            cursor = self.db_connection.cursor()

            # Delete the leave type from the LeaveTypes table
            delete_query = """
                DELETE FROM LeaveTypes WHERE leave_type_id = ?
            """
            cursor.execute(delete_query, (leave_type_id,))
            self.db_connection.commit()  # Commit the transaction

            if cursor.rowcount > 0:
                return {"status": "Success", "message": "Leave type deleted successfully."}
            else:
                return {"status": "Failure", "message": "No leave type found for the provided Leave Type ID."}

        except odbc.Error as e:
            self.db_connection.rollback()  # Roll back any changes if an error occurs
            return {"status": "Failure", "message": f"Error deleting leave type: {str(e)}"}

        finally:
            cursor.close()  # Close the cursor

    def get_leave_type(self, data):
        """Retrieve details of a specific leave type from the LeaveTypes table."""
        leave_type_id = data.get('leave_type_id')

        if not leave_type_id:
            return {"status": "Failure", "message": "Leave Type ID is required."}

        try:
            cursor = self.db_connection.cursor()

            # Query to get the leave type details
            query = """
                SELECT leave_type_id, leave_type_name, description
                FROM LeaveTypes
                WHERE leave_type_id = ?
            """
            cursor.execute(query, (leave_type_id,))
            result = cursor.fetchone()

            if result:
                leave_type_details = {
                    "leave_type_id": result[0],
                    "leave_type_name": result[1],
                    "description": result[2]
                }
                return {"status": "Success", "data": leave_type_details}
            else:
                return {"status": "Failure", "message": "No leave type found for the provided Leave Type ID."}

        except odbc.Error as e:
            return {"status": "Failure", "message": f"Error retrieving leave type: {str(e)}"}

        finally:
            cursor.close()  # Close the cursor

    def get_all_leave_types(self):
        """Retrieve all leave types from the LeaveTypes table."""
        try:
            cursor = self.db_connection.cursor()

            # Query to get all leave types
            query = """
                SELECT leave_type_id, leave_type_name, description
                FROM LeaveTypes
            """
            cursor.execute(query)
            results = cursor.fetchall()

            leave_types = []
            for result in results:
                leave_types.append({
                    "leave_type_id": result[0],
                    "leave_type_name": result[1],
                    "description": result[2]
                })

            return {"status": "Success", "data": leave_types}

        except odbc.Error as e:
            return {"status": "Failure", "message": f"Error retrieving leave types: {str(e)}"}

        finally:
            cursor.close()  # Close the cursor
