import pypyodbc as odbc  # Import pypyodbc for database operations

class OpManageAnnouncements:
    def __init__(self, db_connection):
        self.db_connection = db_connection  # Store the database connection

    def get_announcement(self, data):

        announcement_id = data.get('announcement_id')
        
        if not announcement_id:
            return {"status": "Failure", "message": "Announcement ID is required."}

        try:
            cursor = self.db_connection.cursor()

            # Query to retrieve the announcement details
            query = """
                SELECT 
                    announcement_id, sender_id, announcement_content, date_posted
                FROM Announcements
                WHERE announcement_id = ?
            """
            cursor.execute(query, (announcement_id,))
            result = cursor.fetchone()

            # Check if the query returned any results
            if result:
                announcement_details = {
                    "announcement_id": result[0],
                    "sender_id": result[1],
                    "announcement_content": result[2],
                    "date_posted": result[3]
                }
                
                return {"status": "Success", "data": announcement_details}
            else:
                return {"status": "Failure", "message": "No announcement found for the provided announcement ID."}

        except odbc.Error as e:
            return {"status": "Failure", "message": f"Error retrieving announcement: {str(e)}"}
        finally:
            cursor.close()  # Close the cursor

    def add_announcement(self, data):

        required_fields = ['sender_id', 'announcement_content', 'date_posted']
        
        # Check for missing fields
        for field in required_fields:
            if field not in data:
                return {"status": "Failure", "message": f"Missing required field: {field}"}

        try:
            cursor = self.db_connection.cursor()

            # Query to insert a new announcement record
            insert_query = """
                INSERT INTO Announcements 
                (sender_id, announcement_content, date_posted)
                VALUES (?, ?, ?)
            """
            cursor.execute(insert_query, (
                data['sender_id'],
                data['announcement_content'],
                data['date_posted']
            ))
            self.db_connection.commit()  # Commit the transaction

            return {"status": "Success", "message": "Announcement added successfully."}

        except odbc.Error as e:
            self.db_connection.rollback()  # Roll back any changes if an error occurs
            return {"status": "Failure", "message": f"Error adding announcement: {str(e)}"}
        finally:
            cursor.close()  # Close the cursor

    def update_announcement(self, data):

        announcement_id = data.get('announcement_id')
        sender_id = data.get('sender_id')
        announcement_content = data.get('announcement_content')
        date_posted = data.get('date_posted')

        if not announcement_id:
            return {"status": "Failure", "message": "Announcement ID is required."}

        if not (sender_id or announcement_content or date_posted):
            return {"status": "Failure", "message": "At least one field to update must be provided."}

        try:
            cursor = self.db_connection.cursor()

            # Dynamically build the SQL update query
            update_query = "UPDATE Announcements SET "
            update_fields = []
            update_values = []

            if sender_id:
                update_fields.append("sender_id = ?")
                update_values.append(sender_id)
            if announcement_content:
                update_fields.append("announcement_content = ?")
                update_values.append(announcement_content)
            if date_posted:
                update_fields.append("date_posted = ?")
                update_values.append(date_posted)

            update_query += ", ".join(update_fields)
            update_query += " WHERE announcement_id = ?"
            update_values.append(announcement_id)

            cursor.execute(update_query, tuple(update_values))
            self.db_connection.commit()  # Commit the transaction

            if cursor.rowcount > 0:
                return {"status": "Success", "message": "Announcement updated successfully."}
            else:
                return {"status": "Failure", "message": "No announcement found for the provided announcement ID."}

        except odbc.Error as e:
            self.db_connection.rollback()  # Roll back any changes if an error occurs
            return {"status": "Failure", "message": f"Error updating announcement: {str(e)}"}
        finally:
            cursor.close()  # Close the cursor

    def delete_announcement(self, data):

        announcement_id = data.get('announcement_id')

        if not announcement_id:
            return {"status": "Failure", "message": "Announcement ID is required."}

        try:
            cursor = self.db_connection.cursor()

            # Query to delete the announcement record
            delete_query = """
                DELETE FROM Announcements
                WHERE announcement_id = ?
            """
            cursor.execute(delete_query, (announcement_id,))
            self.db_connection.commit()  # Commit the transaction

            if cursor.rowcount > 0:
                return {"status": "Success", "message": "Announcement deleted successfully."}
            else:
                return {"status": "Failure", "message": "No announcement found for the provided announcement ID."}

        except odbc.Error as e:
            self.db_connection.rollback()  # Roll back any changes if an error occurs
            return {"status": "Failure", "message": f"Error deleting announcement: {str(e)}"}
        finally:
            cursor.close()  # Close the cursor
