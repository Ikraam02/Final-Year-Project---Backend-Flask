import pypyodbc as odbc

class OpManagePerformanceEvaluations:
    def __init__(self, db_connection):
        self.db_connection = db_connection  # Store the database connection

    def add_performance_evaluation(self, data):
        """Add a new performance evaluation to the PerformanceEvaluations table."""
        required_fields = ['employee_id', 'evaluation_date', 'evaluator_id', 'self_assessment', 'feedback', 'overall_rating']

        # Check for missing fields
        for field in required_fields:
            if field not in data:
                return {"status": "Failure", "message": f"Missing required field: {field}"}

        try:
            cursor = self.db_connection.cursor()

            # Check if the employee_id exists in the Employees table
            check_employee_query = "SELECT COUNT(*) FROM Employees WHERE employee_id = ?"
            cursor.execute(check_employee_query, (data['employee_id'],))
            employee_exists = cursor.fetchone()[0]

            if employee_exists == 0:
                return {"status": "Failure", "message": f"Employee with ID '{data['employee_id']}' does not exist."}

            # Check if the evaluator_id exists in the Employees table
            cursor.execute(check_employee_query, (data['evaluator_id'],))
            evaluator_exists = cursor.fetchone()[0]

            if evaluator_exists == 0:
                return {"status": "Failure", "message": f"Evaluator with ID '{data['evaluator_id']}' does not exist."}

            # Insert a new performance evaluation into the PerformanceEvaluations table
            insert_query = """
                INSERT INTO PerformanceEvaluations (employee_id, evaluation_date, evaluator_id, self_assessment, feedback, overall_rating)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(insert_query, (
                data['employee_id'],
                data['evaluation_date'],
                data['evaluator_id'],
                data['self_assessment'],
                data['feedback'],
                data['overall_rating']
            ))
            self.db_connection.commit()  # Commit the transaction

            return {"status": "Success", "message": "Performance evaluation added successfully."}

        except odbc.Error as e:
            self.db_connection.rollback()  # Roll back any changes if an error occurs
            return {"status": "Failure", "message": f"Error adding performance evaluation: {str(e)}"}

        finally:
            cursor.close()  # Close the cursor

    def update_performance_evaluation(self, data):
        """Update an existing performance evaluation in the PerformanceEvaluations table."""
        evaluation_id = data.get('evaluation_id')
        employee_id = data.get('employee_id')
        evaluation_date = data.get('evaluation_date')
        evaluator_id = data.get('evaluator_id')
        self_assessment = data.get('self_assessment')
        feedback = data.get('feedback')
        overall_rating = data.get('overall_rating')

        if not evaluation_id:
            return {"status": "Failure", "message": "Evaluation ID is required."}

        try:
            cursor = self.db_connection.cursor()

            # Dynamically build the SQL update query
            update_query = "UPDATE PerformanceEvaluations SET "
            update_fields = []
            update_values = []

            if employee_id:
                update_fields.append("employee_id = ?")
                update_values.append(employee_id)
            if evaluation_date:
                update_fields.append("evaluation_date = ?")
                update_values.append(evaluation_date)
            if evaluator_id:
                update_fields.append("evaluator_id = ?")
                update_values.append(evaluator_id)
            if self_assessment:
                update_fields.append("self_assessment = ?")
                update_values.append(self_assessment)
            if feedback:
                update_fields.append("feedback = ?")
                update_values.append(feedback)
            if overall_rating:
                update_fields.append("overall_rating = ?")
                update_values.append(overall_rating)

            update_query += ", ".join(update_fields)
            update_query += " WHERE evaluation_id = ?"
            update_values.append(evaluation_id)

            cursor.execute(update_query, tuple(update_values))
            self.db_connection.commit()  # Commit the transaction

            if cursor.rowcount > 0:
                return {"status": "Success", "message": "Performance evaluation updated successfully."}
            else:
                return {"status": "Failure", "message": "No performance evaluation found for the provided Evaluation ID."}

        except odbc.Error as e:
            self.db_connection.rollback()  # Roll back any changes if an error occurs
            return {"status": "Failure", "message": f"Error updating performance evaluation: {str(e)}"}

        finally:
            cursor.close()  # Close the cursor

    def delete_performance_evaluation(self, data):
        """Delete a performance evaluation from the PerformanceEvaluations table."""
        evaluation_id = data.get('evaluation_id')

        if not evaluation_id:
            return {"status": "Failure", "message": "Evaluation ID is required."}

        try:
            cursor = self.db_connection.cursor()

            # Delete the performance evaluation from the PerformanceEvaluations table
            delete_query = """
                DELETE FROM PerformanceEvaluations WHERE evaluation_id = ?
            """
            cursor.execute(delete_query, (evaluation_id,))
            self.db_connection.commit()  # Commit the transaction

            if cursor.rowcount > 0:
                return {"status": "Success", "message": "Performance evaluation deleted successfully."}
            else:
                return {"status": "Failure", "message": "No performance evaluation found for the provided Evaluation ID."}

        except odbc.Error as e:
            self.db_connection.rollback()  # Roll back any changes if an error occurs
            return {"status": "Failure", "message": f"Error deleting performance evaluation: {str(e)}"}

        finally:
            cursor.close()  # Close the cursor

    def get_performance_evaluation(self, data):
        """Retrieve details of a specific performance evaluation from the PerformanceEvaluations table."""
        evaluation_id = data.get('evaluation_id')

        if not evaluation_id:
            return {"status": "Failure", "message": "Evaluation ID is required."}

        try:
            cursor = self.db_connection.cursor()

            # Query to get the performance evaluation details
            query = """
                SELECT evaluation_id, employee_id, evaluation_date, evaluator_id, self_assessment, feedback, overall_rating
                FROM PerformanceEvaluations
                WHERE evaluation_id = ?
            """
            cursor.execute(query, (evaluation_id,))
            result = cursor.fetchone()

            if result:
                evaluation_details = {
                    "evaluation_id": result[0],
                    "employee_id": result[1],
                    "evaluation_date": result[2],
                    "evaluator_id": result[3],
                    "self_assessment": result[4],
                    "feedback": result[5],
                    "overall_rating": result[6]
                }
                return {"status": "Success", "data": evaluation_details}
            else:
                return {"status": "Failure", "message": "No performance evaluation found for the provided Evaluation ID."}

        except odbc.Error as e:
            return {"status": "Failure", "message": f"Error retrieving performance evaluation: {str(e)}"}

        finally:
            cursor.close()  # Close the cursor

    def get_all_performance_evaluations(self):
        """Retrieve all performance evaluations from the PerformanceEvaluations table."""
        try:
            cursor = self.db_connection.cursor()

            # Query to get all performance evaluations
            query = """
                SELECT evaluation_id, employee_id, evaluation_date, evaluator_id, self_assessment, feedback, overall_rating
                FROM PerformanceEvaluations
            """
            cursor.execute(query)
            results = cursor.fetchall()

            evaluations = []
            for result in results:
                evaluations.append({
                    "evaluation_id": result[0],
                    "employee_id": result[1],
                    "evaluation_date": result[2],
                    "evaluator_id": result[3],
                    "self_assessment": result[4],
                    "feedback": result[5],
                    "overall_rating": result[6]
                })

            return {"status": "Success", "data": evaluations}

        except odbc.Error as e:
            return {"status": "Failure", "message": f"Error retrieving performance evaluations: {str(e)}"}

        finally:
            cursor.close()  # Close the cursor
