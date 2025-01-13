import pypyodbc as odbc
import json
from datetime import datetime

class OpPerformanceEvaluation:
    def __init__(self, db_connection):
        self.db_connection = db_connection


class OpPerformanceEvaluation:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def submit_review(self, data):
        # Extract relevant data from the request
        employee_id = data.get('employee_id')
        evaluator_id = data.get('evaluator_id')
        leadership = data.get('leadership')
        teamwork = data.get('teamwork')
        communication_skills = data.get('communication_skills')
        dependability = data.get('dependability', None)
        problem_solving = data.get('problem_solving')
        technical_skills = data.get('technical_skills', None)  # Default to None if not provided
        goal_achievement = data.get('goal_achievement', None)    # Default to None if not provided
        comments = data.get('comments', '')
        evaluation_type = data.get('evaluation_type')

        if not employee_id or not evaluator_id or not evaluation_type:
            return {
                "status": "Failure",
                "message": "Employee ID, Evaluator ID, and Evaluation Type are required."
            }

        if evaluation_type not in ['Self', 'Peer', 'Manager']:
            return {
                "status": "Failure",
                "message": "Invalid Evaluation Type. Must be 'Self', 'Peer', or 'Manager'."
            }

        ratings = [leadership, teamwork, communication_skills, dependability, problem_solving, technical_skills, goal_achievement]
        for rating in ratings:
            if rating is not None and (rating < 1 or rating > 5):
                return {
                    "status": "Failure",
                    "message": "Ratings must be between 1 and 5."
                }

        current_year = datetime.now().year
        check_query = """
        SELECT COUNT(*) FROM ReviewForm
        WHERE employee_id = ? AND evaluator_id = ? AND evaluation_type = ?
        AND YEAR(date_submitted) = ?;
        """
        cursor = self.db_connection.cursor()
        try:
            cursor.execute(check_query, (employee_id, evaluator_id, evaluation_type, current_year))
            review_count = cursor.fetchone()[0]
            if review_count > 0:
                return {
                    "status": "Failure",
                    "message": f"A {evaluation_type} review has already been submitted for {current_year}."
                }
            # Create the insert query
            insert_query = """
            INSERT INTO ReviewForm (employee_id, evaluator_id, leadership, teamwork, communication_skills, dependability, technical_skills, 
            problem_solving, goal_achievement, comments, evaluation_type, date_submitted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """
            # Prepare the data for the query
            values = (
                employee_id,
                evaluator_id,
                leadership,
                teamwork,
                communication_skills,
                dependability,
                technical_skills,
                problem_solving,
                goal_achievement,
                comments,
                evaluation_type,
                datetime.now()  # Use the current timestamp for date_submitted
            )

            # Execute the insert query
            cursor.execute(insert_query, values)
            self.db_connection.commit()  # Commit the transaction
            return {
                "status": "Success",
                "message": "Review submitted successfully."
            }
        except odbc.Error as e:
            self.db_connection.rollback()  # Rollback in case of error
            return {
                "status": "Failure",
                "message": f"Database error: {e}"
            }
        finally:
            cursor.close()


    def get_employee_feedback_by_year(self, employee_id):
        # Get the current year
        current_year = datetime.now().year
        # SQL query to retrieve all reviews for the given employee_id and current year
        query = """
        SELECT review_id, evaluator_id, leadership, teamwork, communication_skills, dependability, technical_skills, 
               problem_solving, goal_achievement, comments, evaluation_type, date_submitted
        FROM ReviewForm
        WHERE employee_id = ? AND YEAR(date_submitted) = ?;
        """
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(query, (employee_id, current_year))
            feedback_records = cursor.fetchall()
            # If no feedback records are found, return an appropriate message
            if not feedback_records:
                return {
                    "status": "Failure",
                    "message": f"No feedback found for employee_id {employee_id} in the year {current_year}."
                }
            # Parse the result into a list of dictionaries
            feedback_list = []
            for row in feedback_records:
                feedback = {
                    "review_id": row[0],
                    "evaluator_id": row[1],
                    "leadership": row[2],
                    "teamwork": row[3],
                    "communication_skills": row[4],
                    "dependability": row[5],
                    "technical_skills": row[6],
                    "problem_solving": row[7],
                    "goal_achievement": row[8],
                    "comments": row[9],
                    "evaluation_type": row[10],
                    "date_submitted": row[11]
                }
                feedback_list.append(feedback)

            return {
                "status": "Success",
                "feedback": feedback_list
            }

        except odbc.Error as e:
            return {
                "status": "Failure",
                "message": f"Database error: {e}"
            }
        finally:
            cursor.close()


    def calculate_appraisal(self, employee_id):
        # Check if appraisal has already been calculated for the current year
        current_year = datetime.now().year
        check_appraisal_sql = """
        SELECT 1 FROM Appraisals 
        WHERE employee_id = ? AND YEAR(appraisal_date) = ?;
        """
        cursor = self.db_connection.cursor()
        cursor.execute(check_appraisal_sql, (employee_id, current_year))
        appraisal_exists = cursor.fetchone() 
        if appraisal_exists:
            cursor.close()
            return {
                "status": "Error",
                "message": "Appraisal has already been calculated for this year."
            }
        
        # Fetch feedback for all types of evaluations (Self, Peer, Manager) for the current year
        sql = """
        SELECT leadership, teamwork, communication_skills, dependability, problem_solving, technical_skills, goal_achievement, evaluation_type
        FROM ReviewForm
        WHERE employee_id = ? AND YEAR(date_submitted) = ?;
        """
        
        cursor.execute(sql, (employee_id, current_year))
        feedback_records = cursor.fetchall()

        # Verify if we have all 3 types of reviews for this employee
        review_types = set([record[-1] for record in feedback_records])  # Get the evaluation types from the records
        required_reviews = {"Self", "Peer", "Manager"}

        if not required_reviews.issubset(review_types):
            missing_reviews = required_reviews - review_types
            cursor.close()
            return {
                "status": "Error",
                "message": f"Missing review(s): {', '.join(missing_reviews)}. All review types (Self, Peer, Manager) are required for appraisal calculation."
            }

        # Initialize sums and count for each competency
        competencies = {
            "leadership": {"sum": 0, "count": 0},
            "teamwork": {"sum": 0, "count": 0},
            "communication_skills": {"sum": 0, "count": 0},
            "dependability": {"sum": 0, "count": 0},
            "problem_solving": {"sum": 0, "count": 0},
            "technical_skills": {"sum": 0, "count": 0},
            "goal_achievement": {"sum": 0, "count": 0}
        }

        # Define weightage for self, peer, and manager reviews
        weightage = {
            "Self": 0.2,
            "Peer": 0.3,
            "Manager": 0.5
        }

        # Aggregate scores for each competency
        for record in feedback_records:
            leadership, teamwork, communication_skills, dependability, problem_solving, technical_skills, goal_achievement, evaluation_type = record

            for competency, score in zip(competencies.keys(), [leadership, teamwork, communication_skills, dependability, 
                                                               problem_solving, technical_skills, goal_achievement]):
                if score is not None:
                    competencies[competency]["sum"] += score * weightage.get(evaluation_type, 1)  # Apply weightage based on evaluation type
                    competencies[competency]["count"] += weightage.get(evaluation_type, 1)

        # Calculate average scores for each competency
        scores = {key: (value["sum"] / value["count"]) if value["count"] > 0 else None for key, value in competencies.items()}

        # Insert calculated scores into PerformanceScore table
        insert_query = """
        INSERT INTO ScorePerformance (employee_id, leadership_score, teamwork_score, communication_skills_score, dependability_score,
          problem_solving_score, technical_skills_score, goal_achievement_score, calculated_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        
        values = (
            employee_id,
            scores["leadership"],
            scores["teamwork"],
            scores["communication_skills"],
            scores["dependability"],
            scores["problem_solving"],
            scores["technical_skills"],
            scores["goal_achievement"],
            datetime.now()
        )
        
        cursor.execute(insert_query, values)
        self.db_connection.commit()

        # Now, calculate the final score (average of non-null competency scores)
        total_score = sum([score for score in scores.values() if score is not None])
        final_score = total_score / len([score for score in scores.values() if score is not None]) if total_score > 0 else 0

        # Appraisal rules based on final score
        salary_increase = 0
        bonus = 0
        promotion_eligible = False

        if final_score >= 4.0:
            salary_increase = 10  # 10% salary increase
            bonus = 5000          # $5000 bonus
            promotion_eligible = True
        elif final_score >= 3.0:
            salary_increase = 5   # 5% salary increase
            bonus = 2000
        else:
            salary_increase = 0
            bonus = 0

        # Insert appraisal result into Appraisals table
        insert_appraisal_query = """
        INSERT INTO Appraisals (employee_id, final_score, salary_increase, bonus, promotion_eligible, appraisal_date)
        VALUES (?, ?, ?, ?, ?, ?);
        """
        
        appraisal_values = (
            employee_id,
            final_score,
            salary_increase,
            bonus,
            promotion_eligible,
            datetime.now()
        )
        
        cursor.execute(insert_appraisal_query, appraisal_values)
        self.db_connection.commit()
        
        cursor.close()

        return {
            "status": "Success",
            "message": "Appraisal calculated successfully.",
            "final_score": final_score,
            "salary_increase": salary_increase,
            "bonus": bonus,
            "promotion_eligible": promotion_eligible
        }


    def generate_report(self, employee_id):
        cursor = self.db_connection.cursor()
        current_year = datetime.now().year

        try:
            # Fetch employee profile details from Users, Employees, and Roles tables
            profile_query = """
            SELECT u.username, u.email, e.first_name, e.last_name, r.role_name, r.description AS department_name
            FROM Users u
            JOIN Employees e ON u.employee_id = e.employee_id
            JOIN Roles r ON u.role_id = r.role_id
            WHERE u.employee_id = ?;
            """
            cursor.execute(profile_query, (employee_id,))
            profile_record = cursor.fetchone()

            if not profile_record:
                return {
                    "status": "Failure",
                    "message": f"No profile found for employee_id {employee_id}."
                }

            # Parse profile details
            profile_details = {
                "username": profile_record[0],
                "email": profile_record[1],
                "first_name": profile_record[2],
                "last_name": profile_record[3],
                "role_name": profile_record[4],
                "department_name": profile_record[5]
            }

            # Fetch performance feedback for the employee
            feedback_query = """
            SELECT leadership, teamwork, communication_skills, dependability, problem_solving, technical_skills, 
                goal_achievement, evaluation_type, comments, date_submitted
            FROM ReviewForm
            WHERE employee_id = ? AND YEAR(date_submitted) = ?;
            """
            cursor.execute(feedback_query, (employee_id, current_year))
            feedback_records = cursor.fetchall()

            if not feedback_records:
                return {
                    "status": "Failure",
                    "message": f"No feedback found for employee_id {employee_id} in {current_year}."
                }

            # Parse the feedback into a list of dictionaries
            feedback_list = []
            for row in feedback_records:
                feedback = {
                    "leadership": row[0],
                    "teamwork": row[1],
                    "communication_skills": row[2],
                    "dependability": row[3],
                    "problem_solving": row[4],
                    "technical_skills": row[5],
                    "goal_achievement": row[6],
                    "evaluation_type": row[7],
                    "comments": row[8],
                    "date_submitted": row[9].strftime('%Y-%m-%d %H:%M:%S')
                }
                feedback_list.append(feedback)

            # Fetch performance score for the employee
            score_query = """
            SELECT leadership_score, teamwork_score, communication_skills_score, dependability_score, 
                problem_solving_score, technical_skills_score, goal_achievement_score, calculated_date
            FROM ScorePerformance
            WHERE employee_id = ? AND YEAR(calculated_date) = ?;
            """
            cursor.execute(score_query, (employee_id, current_year))
            score_record = cursor.fetchone()

            if not score_record:
                return {
                    "status": "Failure",
                    "message": f"No performance score found for employee_id {employee_id} in {current_year}."
                }

            # Parse performance score
            performance_scores = {
                "leadership_score": round(score_record[0], 2),
                "teamwork_score": round(score_record[1], 2),
                "communication_skills_score": round(score_record[2], 2),
                "dependability_score": round(score_record[3], 2),
                "problem_solving_score": round(score_record[4], 2),
                "technical_skills_score": round(score_record[5], 2),
                "goal_achievement_score": score_record[6],
                "calculated_date": score_record[7].strftime('%Y-%m-%d %H:%M:%S')
            }

            # Fetch appraisal details for the employee
            appraisal_query = """
            SELECT final_score, salary_increase, bonus, promotion_eligible, appraisal_date
            FROM Appraisals
            WHERE employee_id = ? AND YEAR(appraisal_date) = ?;
            """
            cursor.execute(appraisal_query, (employee_id, current_year))
            appraisal_record = cursor.fetchone()

            if not appraisal_record:
                return {
                    "status": "Failure",
                    "message": f"No appraisal found for employee_id {employee_id} in {current_year}."
                }

            # Parse appraisal data
            appraisal_details = {
                "final_score": round(appraisal_record[0], 2),
                "salary_increase": appraisal_record[1],
                "bonus": appraisal_record[2],
                "promotion_eligible": bool(appraisal_record[3]),
                "appraisal_date": appraisal_record[4].strftime('%Y-%m-%d %H:%M:%S')
            }

            # Return a comprehensive report with profile details
            return {
                "status": "Success",
                "report": {
                    "employee_id": employee_id,
                    "year": current_year,
                    "profile_details": profile_details,  # Add profile details here
                    "feedback": feedback_list,
                    "performance_scores": performance_scores,
                    "appraisal_details": appraisal_details
                }
            }

        except odbc.Error as e:
            return {
                "status": "Failure",
                "message": f"Database error: {e}"
            }

        finally:
            cursor.close()

