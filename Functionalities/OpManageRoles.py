import pypyodbc as odbc

class OpManageRoles:
    def __init__(self, db_connection):
        self.db_connection = db_connection  # Store the database connection


    def add_role(self, data):
        """Add a new role to the Roles table, ensuring the role_name is unique."""
        required_fields = ['role_name', 'description', 'salary']

        # Check for missing fields
        for field in required_fields:
            if field not in data:
                return {"status": "Failure", "message": f"Missing required field: {field}"}

        try:
            cursor = self.db_connection.cursor()

            # Check if the role_name already exists
            check_query = "SELECT COUNT(*) FROM Roles WHERE role_name = ?"
            cursor.execute(check_query, (data['role_name'],))
            existing_role_count = cursor.fetchone()[0]

            if existing_role_count > 0:
                return {"status": "Failure", "message": f"Role with name '{data['role_name']}' already exists."}

            # Insert a new role into the Roles table
            insert_query = """
                INSERT INTO Roles (role_name, description, salary)
                VALUES (?, ?, ?)
            """
            cursor.execute(insert_query, (
                data['role_name'],
                data['description'],
                data['salary']
            ))
            self.db_connection.commit()  # Commit the transaction

            return {"status": "Success", "message": "Role added successfully."}

        except odbc.Error as e:
            self.db_connection.rollback()  # Roll back any changes if an error occurs
            return {"status": "Failure", "message": f"Error adding role: {str(e)}"}

        finally:
            cursor.close()  # Close the cursor


    def update_role(self, data):
        role_id = data.get('role_id')
        role_name = data.get('role_name')
        description = data.get('description')
        salary = data.get('salary')

        if not role_id:
            return {"status": "Failure", "message": "Role ID is required."}

        if not (role_name or description or salary):
            return {"status": "Failure", "message": "At least one field to update must be provided."}

        try:
            cursor = self.db_connection.cursor()
            update_query = "UPDATE Roles SET "
            update_fields = []
            update_values = []

            if role_name:
                update_fields.append("role_name = ?")
                update_values.append(role_name)
            if description:
                update_fields.append("description = ?")
                update_values.append(description)
            if salary:
                update_fields.append("salary = ?")
                update_values.append(salary)

            update_query += ", ".join(update_fields)
            update_query += " WHERE role_id = ?"
            update_values.append(role_id)

            cursor.execute(update_query, tuple(update_values))
            self.db_connection.commit()  # Commit the transaction

            if cursor.rowcount > 0:
                return {"status": "Success", "message": "Role updated successfully."}
            else:
                return {"status": "Failure", "message": "No role found for the provided Role ID."}

        except odbc.Error as e:
            self.db_connection.rollback()  # Roll back any changes if an error occurs
            return {"status": "Failure", "message": f"Error updating role: {str(e)}"}

        finally:
            cursor.close()  # Close the cursor

    def delete_role(self, data):
        """Delete a role from the Roles table."""
        role_id = data.get('role_id')

        if not role_id:
            return {"status": "Failure", "message": "Role ID is required."}

        try:
            cursor = self.db_connection.cursor()

            # Delete the role from the Roles table
            delete_query = """
                DELETE FROM Roles WHERE role_id = ?
            """
            cursor.execute(delete_query, (role_id,))
            self.db_connection.commit()  # Commit the transaction

            if cursor.rowcount > 0:
                return {"status": "Success", "message": "Role deleted successfully."}
            else:
                return {"status": "Failure", "message": "No role found for the provided Role ID."}

        except odbc.Error as e:
            self.db_connection.rollback()  # Roll back any changes if an error occurs
            return {"status": "Failure", "message": f"Error deleting role: {str(e)}"}

        finally:
            cursor.close()  # Close the cursor

    def get_role(self, data):
        """Retrieve details of a specific role from the Roles table."""
        role_id = data.get('role_id')

        if not role_id:
            return {"status": "Failure", "message": "Role ID is required."}

        try:
            cursor = self.db_connection.cursor()

            # Query to get the role details
            query = """
                SELECT role_id, role_name, description, salary
                FROM Roles
                WHERE role_id = ?
            """
            cursor.execute(query, (role_id,))
            result = cursor.fetchone()

            if result:
                role_details = {
                    "role_id": result[0],
                    "role_name": result[1],
                    "description": result[2],
                    "salary": result[3]
                }
                return {"status": "Success", "data": role_details}
            else:
                return {"status": "Failure", "message": "No role found for the provided Role ID."}

        except odbc.Error as e:
            return {"status": "Failure", "message": f"Error retrieving role: {str(e)}"}

        finally:
            cursor.close()  # Close the cursor

    def get_all_roles(self):
        """Retrieve all roles from the Roles table."""
        try:
            cursor = self.db_connection.cursor()

            # Query to get all roles
            query = """
                SELECT role_id, role_name, description, salary
                FROM Roles
            """
            cursor.execute(query)
            results = cursor.fetchall()

            roles = []
            for result in results:
                roles.append({
                    "role_id": result[0],
                    "role_name": result[1],
                    "description": result[2],
                    "salary": result[3]
                })

            return {"status": "Success", "data": roles}

        except odbc.Error as e:
            return {"status": "Failure", "message": f"Error retrieving roles: {str(e)}"}

        finally:
            cursor.close()  # Close the cursor
            