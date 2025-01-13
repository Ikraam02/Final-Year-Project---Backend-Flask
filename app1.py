from flask import Flask, request, jsonify, session
import pypyodbc as odbc
from flask_cors import CORS  # Import CORS
from datetime import timedelta
from Functionalities.OpAddUserEmployee import OpAddUserEmployee
from Functionalities.OpApplyForLeave import OpApplyLeave
from Functionalities.OpApproveLeave import OpApproveLeave  #736
from Functionalities.OpRejectLeave import OpRejectLeave
from Functionalities.OpDeleteUserEmployee import OpDeleteUserEmployee
from Functionalities.OpCheckLeaveBalance import OpCheckLeaveBalance
from Functionalities.OpEditPassword import OpEditPassword
from Functionalities.OpEditProfile import OpEditProfile
from Functionalities.OpGetAllEmployees import OpGetAllEmployees #472
from Functionalities.OpGetAllUsers import OpGetAllUsers
from Functionalities.OpLogin import OpLogin
from Functionalities.OpManageRoles import OpManageRoles
from Functionalities.OpPublishAnnouncements import OpManageAnnouncements # 1719
from Functionalities.OpMonitorAttendance import OpMonitorAttendance
from Functionalities.OpGenerateAttendanceRep import OpGenerateAttendanceReport
from Functionalities.OpPerformanceEvaluation import OpPerformanceEvaluation
from Functionalities.OpReadUserEmployee import OpGetEmployeeById
from Functionalities.OpTrackLeaveHistory import OpTrackLeaveHistory
from Functionalities.OpUpdateUserEmployee import OpUpdateUserEmployee
from Functionalities.OpViewProfile import OpViewProfile #683
from Functionalities.OpProcessPayroll import OpManagePayroll
from Functionalities.OpGetAllCompetencies import OpGetAllCompetencies
from Functionalities.OpHrDashboard import OpHrDashboard
from Functionalities.OpEmployeeDashboard import OpEmployeeDashboard

# Database connection string
connection_string = """
    DRIVER={SQL SERVER};
    SERVER=DESKTOP-G4A2LDV;
    DATABASE=HRMS;
    Trust_Connection=yes;
"""

# Create a database connection
def create_db_connection():
    try:
        connection = odbc.connect(connection_string)
        print("Database connection successful")
        return connection
    except odbc.Error as e:
        print("Database connection error:", e)
        return None

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes by default
app.secret_key = 'your_strong_secret_key'
app.permanent_session_lifetime = timedelta(minutes=30)


#CORS(app, resources={r"/process": {"origins": "http://example.com"}})

@app.route('/process', methods = ['POST'])
def process():
    if request.method == "POST":
        data = request.json
        operation_code = data.get('operationCode')

        # Create a database connection
        db_connection = create_db_connection()
        if not db_connection:
            return jsonify({"status": "Failure", "message": "Database connection failed."}), 500
        
        if operation_code == "OpHrDashboard":
            hr_dashbpard = OpHrDashboard(db_connection)
            result = hr_dashbpard.hr_dashboard()  # Call the method to add a user
            if db_connection:
                db_connection.close()

            return jsonify(result)
        
        elif operation_code == "OpEmployeeDashboard":
            employee_dashbpard = OpEmployeeDashboard(db_connection)
            employee_id = data.get("employee_id")
            result = employee_dashbpard.employee_dashboard(employee_id)  # Call the method to add a user
            if db_connection:
                db_connection.close()

            return jsonify(result)
        
        elif operation_code == "OpGetTotalUsers":
            get_total_users = OpHrDashboard(db_connection)
            result = get_total_users.get_total_users()  # Call the method to add a user
            if db_connection:
                db_connection.close()

            return jsonify(result)

        elif operation_code == "OpGetEmployeesOnLeave":
            get_employees_on_leave = OpHrDashboard(db_connection)
            result = get_employees_on_leave.get_employees_on_leave_today()  # Call the method to add a user
            if db_connection:
                db_connection.close()

            return jsonify(result)

        elif operation_code == "OpGetTotalSalary":
            get_total_salary = OpHrDashboard(db_connection)
            result = get_total_salary.get_total_net_salary_previous_month()  # Call the method to add a user
            if db_connection:
                db_connection.close()

            return jsonify(result)

        elif operation_code == "OpGetTotalPresent":
            get_total_present = OpHrDashboard(db_connection)
            result = get_total_present.get_total_employees_clocked_in_today()  # Call the method to add a user
            if db_connection:
                db_connection.close()
            return jsonify(result)
        
        elif operation_code == "OpGetPercentageDepartment":
            get_percentage_dep = OpHrDashboard(db_connection)
            result = get_percentage_dep.get_total_users_and_it_department_users()  # Call the method to add a user
            if db_connection:
                db_connection.close()

            return jsonify(result)

        elif operation_code == "OpAddUserEmployee":
            add_user_employee = OpAddUserEmployee(db_connection)
            result = add_user_employee.add_user(data)  # Call the method to add a user
            if db_connection:
                db_connection.close()

            return jsonify(result)
        
        elif operation_code == "OpGetAllUsers":
            get_all_users = OpGetAllUsers(db_connection)
            result = get_all_users.get_all_users()  # Call the method to add a user
            if db_connection:
                db_connection.close()

            return jsonify(result)
        
        elif operation_code == "OpGetUsersInSameDepartment":
            get_all_users_in_department = OpGetAllUsers(db_connection)
            employee_id = data.get('employee_id')
            result = get_all_users_in_department.get_users_in_same_department(employee_id)  # Call the method to add a user
            if db_connection:
                db_connection.close()

            return jsonify(result)
        

        elif operation_code == "OpGetAllUsersAttendance":
            get_all_users = OpGetAllUsers(db_connection)
            result = get_all_users.get_all_users_for_attendance_report()  # Call the method to add a user
            if db_connection:
                db_connection.close()

            return jsonify(result)
        
        elif operation_code == "OpGetEmployeesWithNoLeaveBalance":
            leave_balance_checker = OpCheckLeaveBalance(db_connection)
            result = leave_balance_checker.get_all_employees_with_no_leave_balance()
            if db_connection:
                db_connection.close()

            return jsonify(result)
        
        elif operation_code == "OpGetEmployeesWithLeaveBalance":
            leave_balance_checker = OpCheckLeaveBalance(db_connection)
            result = leave_balance_checker.get_employees_with_leave_balance()
            if db_connection:
                db_connection.close()

            return jsonify(result)
        
        elif operation_code == "OpGetAllCompetencies":
            get_all_competencies = OpGetAllCompetencies(db_connection)
            if db_connection:
                db_connection.close()

            result = get_all_competencies.get_all_competencies()
            return jsonify(result)


        elif operation_code == "OpApplyForLeave":
            apply_leave = OpApplyLeave(db_connection)
            result = apply_leave.apply_leave(data)  # Call the method to add a user
            if db_connection:
                db_connection.close()

            return jsonify(result)
        
        elif operation_code == "OpGetLeaveApplications":
            get_leave_applications = OpApplyLeave(db_connection)
            result = get_leave_applications.get_leave_applications(data.get('employee_id'))  # Call the method to add a user
            if db_connection:
                db_connection.close()

            print(result)
            return jsonify(result)
        
        elif operation_code == "OpGetAllPendingLeaves":
            get_all_pending_leaves = OpApplyLeave(db_connection)
            result = get_all_pending_leaves.get_all_pending_leave_applications()  # Call the method to add a user
            if db_connection:
                db_connection.close()

            return jsonify(result)


        elif operation_code == "OpApproveLeave":
            approve_leave = OpApproveLeave(db_connection)
            result = approve_leave.approve_leave(data)  # Call the method to add a user
            if db_connection:
                db_connection.close()

            return jsonify(result)
        
        elif operation_code == "OpRejectLeave":
            reject_leave = OpRejectLeave(db_connection)
            result = reject_leave.reject_leave(data)  # Call the method to add a user
            if db_connection:
                db_connection.close()
                
            return jsonify(result)

        elif operation_code == "OpSubmitReview":
            submit_review = OpPerformanceEvaluation(db_connection)
            result = submit_review.submit_review(data)
            if db_connection:
                db_connection.close()

            return jsonify(result)
        
        elif operation_code == "OpGetFeedbacks":
            get_feedbacks = OpPerformanceEvaluation(db_connection)
            employee = data.get("employee_id")
            result = get_feedbacks.get_employee_feedback_by_year(employee)
            if db_connection:
                db_connection.close()

            return jsonify(result)

        elif operation_code == "OpCalculateAppraisal":
            calculate_appraisal = OpPerformanceEvaluation(db_connection)
            employee = data.get("employee_id")
            result = calculate_appraisal.calculate_appraisal(employee)
            if db_connection:
                db_connection.close()

            return jsonify(result)


        elif operation_code == "OpGeneratePerformanceReport":
            generate_performance_report = OpPerformanceEvaluation(db_connection)
            employee = data.get("employee_id")
            result = generate_performance_report.generate_report(employee)
            if db_connection:
                db_connection.close()

            return jsonify(result)

    
        elif operation_code == "OpAddLeaveBalance":
            add_leave_balance = OpCheckLeaveBalance(db_connection)
            result = add_leave_balance.add_leave_balance(data)
            if db_connection:
                db_connection.close()

            return jsonify(result)
        
        elif operation_code == "OpCheckLeaveBalance":
            check_leave_balance = OpCheckLeaveBalance(db_connection)
            result = check_leave_balance.get_leave_balance(data)
            if db_connection:
                db_connection.close()

            return jsonify(result)
        
        elif operation_code == "OpDeleteLeaveBalance":
            delete_leave_balance = OpCheckLeaveBalance(db_connection)
            result = delete_leave_balance.delete_leave_balance(data)
            if db_connection:
                db_connection.close()

            return jsonify(result)
        

        
        ##OpManageRoles
        elif operation_code == "OpAddRole":
            add_role = OpManageRoles(db_connection)
            result = add_role.add_role(data)
            if db_connection:
                db_connection.close()

            return jsonify(result)

        elif operation_code == "OpGetRole":
            get_role = OpManageRoles(db_connection)
            result = get_role.get_role(data)
            if db_connection:
                db_connection.close()

            return jsonify(result)
        
        elif operation_code == "OpUpdateRole":
            update_role = OpManageRoles(db_connection)
            result = update_role.update_role(data)
            if db_connection:
                db_connection.close()

            return jsonify(result)
        
        elif operation_code == "OpDeleteRole":
            delete_role = OpManageRoles(db_connection)
            result = delete_role.delete_role(data)
            if db_connection:
                db_connection.close()

            return jsonify(result)
        
        elif operation_code == "OpGetAllRoles":
            get_all_roles = OpManageRoles(db_connection)
            result = get_all_roles.get_all_roles()
            return jsonify(result)


        
        elif operation_code == "OpClockIn":
            public_holidays = ['2024-10-31', '2024-12-25']  
            clock_in = OpMonitorAttendance(db_connection, public_holidays)
            result = clock_in.clock_in(data)
            if db_connection:
                db_connection.close()

            return jsonify(result)


        elif operation_code == "OpClockOut":
            public_holidays = ['2024-10-31', '2024-12-25']  
            clock_out = OpMonitorAttendance(db_connection, public_holidays)
            result = clock_out.clock_out(data)
            if db_connection:
                db_connection.close()

            return jsonify(result)

        elif operation_code == "OpDeleteUserEmployee":
            delete_user_employee = OpDeleteUserEmployee(db_connection)
            result = delete_user_employee.delete_employee(data)
            if db_connection:
                db_connection.close()

            return jsonify(result)

        elif operation_code == "OpEditPassword":
            edit_password = OpEditPassword(db_connection)
            result = edit_password.update_password(data)
            if db_connection:
                db_connection.close()

            return jsonify(result)
      

        elif operation_code == "OpEditProfile":
            edit_employee = OpEditProfile(db_connection)
            result = edit_employee.update_employee_details(data)
            if db_connection:
                db_connection.close()

            return jsonify(result)
      
        elif operation_code == "OpGenerateAttendanceReport":
            public_holidays = ['2024-10-31', '2024-12-25'] 
            generate_attendance_report = OpGenerateAttendanceReport(db_connection, public_holidays)
            result = generate_attendance_report.generate_attendance_report(data)
            if db_connection:
                db_connection.close()

            return jsonify(result)



        elif operation_code == "OpGetAllEmployees":
            get_all_employee = OpGetAllEmployees(db_connection)
            result = get_all_employee.view_all_employees()
            if db_connection:
                db_connection.close()

            return jsonify(result)
        
        if operation_code == "OpLogin":
            login = OpLogin(db_connection)
            result = login.authenticate_user(data)
            if result['status'] == 'Success':
                # Start session on successful login
                session.permanent = True  # Make session permanent (30 minutes by default)
                session['user_id'] = result.get('employee_id')
                session['role'] = result.get('role')

            if db_connection:
                db_connection.close()

            return jsonify(result)
            

        elif operation_code == "OpGenerateAttendanceRow":
            public_holidays = ['2024-10-31', '2024-12-25']  
            add_attendance_row = OpMonitorAttendance(db_connection, public_holidays)
            result = add_attendance_row.generate_attendance_row(data)
            if db_connection:
                db_connection.close()


            return jsonify(result)
        
        elif operation_code == "OpGetMonthlyAttendance":
            print("OpGetMonth")
            public_holidays = ['2024-10-31', '2024-12-25']  
            get_monthly_attendance = OpMonitorAttendance(db_connection, public_holidays)
            result = get_monthly_attendance.get_monthly_attendance(data)
            if db_connection:
                db_connection.close()

            return jsonify(result)
        
        elif operation_code == "OpGetMonthlyAttendanceByData":
            print("OpGetMonth")
            public_holidays = ['2024-10-31', '2024-12-25']  
            get_monthly_attendance = OpMonitorAttendance(db_connection, public_holidays)
            result = get_monthly_attendance.get_monthly_attendance_by_data(data)
            if db_connection:
                db_connection.close()

            return jsonify(result)


        elif operation_code == "OpProcessPayroll":
            add_payroll = OpManagePayroll(db_connection)
            result = add_payroll.add_payroll_record(data)
            if db_connection:
                db_connection.close()

            return jsonify(result)
        
        elif operation_code == "OpGeneratePayrollReport":
            generate_payroll_report = OpManagePayroll(db_connection)
            result = generate_payroll_report.generate_monthly_report(data)
            if db_connection:
                db_connection.close()

            return jsonify(result)
        
        elif operation_code == "OpGetUnprocessedPayrollEmployees":
            get_unprocessed_payroll = OpManagePayroll(db_connection)
            result = get_unprocessed_payroll.OpGetUnprocessedPayrollEmployees()
            if db_connection:
                db_connection.close()

            return jsonify(result)
        
        elif operation_code == "OpGetProcessedPayrollEmployees":
            get_processed_payroll = OpManagePayroll(db_connection)
            result = get_processed_payroll.OpGetProcessedPayrollEmployees()
            print("Result  ", result) 
            if db_connection:
                db_connection.close()

            return jsonify(result)
            
        #OpPublishAnnouncement
        elif operation_code == "OpAddAnnouncement":
            add_announcement = OpManageAnnouncements(db_connection)
            result = add_announcement.add_announcement(data)
            return jsonify(result)
        
        elif operation_code == "OpEditAnnouncement":
            edit_announcement = OpManageAnnouncements(db_connection)
            result = edit_announcement.update_announcement(data)
            return jsonify(result)
        
        elif operation_code == "OpDeleteAnnouncement":
            delete_announcement = OpManageAnnouncements(db_connection)
            result = delete_announcement.delete_announcement(data)
            return jsonify(result)
        
        elif operation_code == "OpGetAnnouncement":
            get_announcement = OpManageAnnouncements(db_connection)
            result = get_announcement.get_announcement(data)
            return jsonify(result)

        elif operation_code == "OpReadUserEmployee":
            get_employee = OpGetEmployeeById(db_connection)
            result = get_employee.get_employee_by_id(data)
            return jsonify(result)

        elif operation_code == "OpPerformanceEvaluation":
            performance_evaluation = OpPerformanceEvaluation(db_connection)
            employee_id = data.get("employee_id")
            result = performance_evaluation.generate_performance_report(employee_id)
            if db_connection:
                db_connection.close()

            return jsonify(result)

        elif operation_code == "OpTrackLeaveHistory":
            track_leave_history = OpTrackLeaveHistory(db_connection)
            result = track_leave_history.get_leave_applications_by_employee(data)  # Call the method to add a user
            if db_connection:
                db_connection.close()

            return jsonify(result)

        elif operation_code == "OpUpdateUserEmployee":
            update_user_employee = OpUpdateUserEmployee(db_connection)
            result = update_user_employee.update_employee(data)  # Call the method to add a user
            if db_connection:
                db_connection.close()

            return jsonify(result)

        elif operation_code == "OpViewProfile":
            view_profile = OpViewProfile(db_connection)
            result = view_profile.view_profile(data)  # Call the method to add a user
            if db_connection:
                db_connection.close()

            return jsonify(result)

        else:
            result = {"status": "Failed", "message": "User deleted successfully."}
            return jsonify(result)
        
        result = {"status": "Success", "message": "User deleted successfully."}
        return jsonify(result)

@app.route('/logout', methods=['POST'])
def logout():
    # Clear session data on logout
    session.clear()
    return jsonify({"status": "Success", "message": "Logged out successfully."})

if __name__ == '__main__':
    app.run(debug = True, port=9000)