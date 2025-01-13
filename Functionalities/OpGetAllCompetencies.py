import pypyodbc as odbc  # Import pypyodbc for database operations

class OpGetAllCompetencies:
    def __init__(self, db_connection):
        self.db_connection = db_connection  # Store the database connectio


    def get_all_competencies(self):
        try:
            cursor = self.db_connection.cursor()

            # Query to retrieve employee_id, username, email, and last_login
            query = """
                SELECT 
                    c.competency_id,
                    c.competency_name, 
                    c.description
                FROM Competencies c
            """
            cursor.execute(query)
            results = cursor.fetchall()

            # Check if the query returned any results
            if results:
                # Map the results to a list of dictionaries
                compentencies = []
                for row in results:
                    compentencies_details = {
                        "competency_id": row[0],
                        "comptency_name": row[1],
                        "description": row[2]
                    }
                    compentencies.append(compentencies_details)
                return {"status": "Success", "data": compentencies}
            else:
                return {"status": "Failure", "message": "No compentencies found."}

        except odbc.Error as e:
            return {"status": "Failure", "message": f"Error retrieving users: {str(e)}"}
        finally:
            cursor.close()

