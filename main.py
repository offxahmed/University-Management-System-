import sys
import datetime
from config import get_connection
import db_init
import seed
from operations import student_ops, teacher_ops, enrollment_ops, attendance_ops, result_ops, transcript_ops

def print_header(title):
    print("\n" + "=" * 50)
    print(f" {title.upper()} ".center(50, "="))
    print("=" * 50)

def pause():
    input("\nPress Enter to continue...")

def handle_init_db():
    print_header("Initialize Database")
    confirm = input("This will drop and recreate the 'university_db' database. Continue? (y/n): ")
    if confirm.lower() == 'y':
        db_init.initialize_all()
    else:
        print("Initialization cancelled.")
    pause()

def handle_seed_data():
    print_header("Seed Sample Data")
    confirm = input("This will seed 10,000 students, 300 courses, 500 teachers, and 100k registrations. Proceed? (y/n): ")
    if confirm.lower() == 'y':
        seed.seed_all()
    else:
        print("Seeding cancelled.")
    pause()

def handle_student_ops(conn):
    while True:
        print_header("Student Operations")
        print("1. Add New Student")
        print("2. Update Student Profile")
        print("3. View Student Profile (Detailed)")
        print("4. List Students")
        print("0. Back to Main Menu")
        
        choice = input("\nEnter choice: ").strip()
        if choice == "1":
            print_header("Add New Student")
            try:
                dept_id = int(input("Department ID: "))
                roll = input("Roll Number: ").strip()
                first = input("First Name: ").strip()
                last = input("Last Name: ").strip()
                email = input("Email: ").strip()
                dob_str = input("Date of Birth (YYYY-MM-DD): ").strip()
                adm_str = input("Admission Date (YYYY-MM-DD): ").strip()
                
                dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d").date()
                adm = datetime.datetime.strptime(adm_str, "%Y-%m-%d").date()
                
                s_id = student_ops.add_student(conn, dept_id, roll, first, last, email, dob, adm)
                print(f"\nStudent successfully added with ID: {s_id}")
            except Exception as e:
                print(f"\nError: {e}")
            pause()
            
        elif choice == "2":
            print_header("Update Student Profile")
            try:
                s_id = int(input("Student ID: "))
                print("Enter fields to update (leave empty to keep current value):")
                roll = input("New Roll Number: ").strip()
                first = input("New First Name: ").strip()
                last = input("New Last Name: ").strip()
                email = input("New Email: ").strip()
                
                fields = {}
                if roll: fields["roll_number"] = roll
                if first: fields["first_name"] = first
                if last: fields["last_name"] = last
                if email: fields["email"] = email
                
                if fields:
                    student_ops.update_student(conn, s_id, **fields)
                    print("\nStudent profile updated successfully.")
                else:
                    print("\nNo fields provided for update.")
            except Exception as e:
                print(f"\nError: {e}")
            pause()
            
        elif choice == "3":
            print_header("View Student Profile")
            try:
                s_id = int(input("Student ID: "))
                student = student_ops.view_student(conn, s_id)
                if student:
                    print("\n--- Student Details ---")
                    for k, v in student.items():
                        print(f"{k.replace('_', ' ').title()}: {v}")
                else:
                    print("\nStudent not found.")
            except Exception as e:
                print(f"\nError: {e}")
            pause()
            
        elif choice == "4":
            print_header("List Students")
            try:
                limit = int(input("Limit (default 50): ") or 50)
                offset = int(input("Offset (default 0): ") or 0)
                students = student_ops.list_students(conn, limit, offset)
                print(f"\nFound {len(students)} students:")
                print(f"{'ID':<6} {'Roll Number':<15} {'Name':<25} {'GPA':<5} {'Standing':<12} {'Dept'}")
                print("-" * 75)
                for s in students:
                    name = f"{s['first_name']} {s['last_name']}"
                    print(f"{s['student_id']:<6} {s['roll_number']:<15} {name:<25} {s['cgpa']:<5} {s['academic_standing']:<12} {s['dept_code']}")
            except Exception as e:
                print(f"\nError: {e}")
            pause()
            
        elif choice == "0":
            break

def handle_teacher_ops(conn):
    while True:
        print_header("Teacher & Course Assignment")
        print("1. Add New Teacher")
        print("2. Assign Course to Teacher")
        print("3. View Teacher Profile & Schedule")
        print("0. Back to Main Menu")
        
        choice = input("\nEnter choice: ").strip()
        if choice == "1":
            print_header("Add New Teacher")
            try:
                dept_id = int(input("Department ID: "))
                first = input("First Name: ").strip()
                last = input("Last Name: ").strip()
                email = input("Email: ").strip()
                hire_str = input("Hire Date (YYYY-MM-DD): ").strip()
                desig = input("Designation (Lecturer/Assistant Professor/Associate Professor/Professor): ").strip()
                
                hire = datetime.datetime.strptime(hire_str, "%Y-%m-%d").date()
                t_id = teacher_ops.add_teacher(conn, dept_id, first, last, email, hire, desig)
                print(f"\nTeacher successfully added with ID: {t_id}")
            except Exception as e:
                print(f"\nError: {e}")
            pause()
            
        elif choice == "2":
            print_header("Assign Course to Teacher")
            try:
                t_id = int(input("Teacher ID: "))
                c_id = int(input("Course ID: "))
                teacher_ops.assign_course(conn, t_id, c_id)
                print("\nCourse successfully assigned to teacher.")
            except Exception as e:
                print(f"\nError: {e}")
            pause()
            
        elif choice == "3":
            print_header("View Teacher Profile")
            try:
                t_id = int(input("Teacher ID: "))
                teacher = teacher_ops.view_teacher(conn, t_id)
                if teacher:
                    print("\n--- Teacher Details ---")
                    for k, v in teacher.items():
                        print(f"{k.replace('_', ' ').title()}: {v}")
                    
                    print("\n--- Course Schedule ---")
                    courses = teacher_ops.get_teacher_schedule(conn, t_id)
                    if courses:
                        print(f"{'Course ID':<10} {'Code':<12} {'Course Name':<30} {'Enrollments'}")
                        print("-" * 65)
                        for c in courses:
                            print(f"{c['course_id']:<10} {c['course_code']:<12} {c['course_name']:<30} {c['current_enrollment']}/{c['max_capacity']}")
                    else:
                        print("No courses assigned to this teacher.")
                else:
                    print("\nTeacher not found.")
            except Exception as e:
                print(f"\nError: {e}")
            pause()
            
        elif choice == "0":
            break

def handle_enroll_student(conn):
    print_header("Enroll Student")
    try:
        s_id = int(input("Student ID: "))
        c_id = int(input("Course ID: "))
        sem_id = int(input("Semester ID: "))
        
        enroll_id = enrollment_ops.enroll_student(conn, s_id, c_id, sem_id)
        print(f"\nStudent successfully enrolled. Enrollment ID: {enroll_id}")
    except Exception as e:
        print(f"\nError: {e}")
    pause()

def handle_attendance_ops(conn):
    while True:
        print_header("Attendance Operations")
        print("1. Mark Single Student Attendance")
        print("2. Mark Bulk Attendance for Class")
        print("3. View Attendance Report")
        print("0. Back to Main Menu")
        
        choice = input("\nEnter choice: ").strip()
        if choice == "1":
            print_header("Mark Attendance")
            try:
                enroll_id = int(input("Enrollment ID: "))
                date_str = input("Date (YYYY-MM-DD, enter for today): ").strip()
                if not date_str:
                    date = datetime.date.today()
                else:
                    date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                status = input("Status (Present/Absent/Late/Excused): ").strip()
                
                att_id = attendance_ops.mark_attendance(conn, enroll_id, date, status)
                print(f"\nAttendance marked successfully. Attendance ID: {att_id}")
            except Exception as e:
                print(f"\nError: {e}")
            pause()
            
        elif choice == "2":
            print_header("Bulk Attendance Marking")
            try:
                c_id = int(input("Course ID: "))
                sem_id = int(input("Semester ID: "))
                date_str = input("Date (YYYY-MM-DD, enter for today): ").strip()
                if not date_str:
                    date = datetime.date.today()
                else:
                    date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                
                # Fetch active class roster
                roster = enrollment_ops.get_course_roster(conn, c_id, sem_id)
                if not roster:
                    print("\nNo active student enrollments found for this course and semester.")
                    pause()
                    continue
                    
                print(f"\nFound {len(roster)} registered students. Mark: (P)resent, (A)bsent, (L)ate, (E)xcused")
                att_list = []
                status_map = {'p': 'Present', 'a': 'Absent', 'l': 'Late', 'e': 'Excused'}
                
                for r in roster:
                    name = f"{r['first_name']} {r['last_name']}"
                    while True:
                        s_input = input(f"Roll: {r['roll_number']} | Name: {name} | Status [P]: ").strip().lower() or 'p'
                        if s_input in status_map:
                            att_list.append((r['student_id'], status_map[s_input]))
                            break
                        print("Invalid status! Use P, A, L, or E.")
                
                attendance_ops.mark_bulk_attendance(conn, c_id, sem_id, date, att_list)
                print("\nBulk attendance submitted successfully.")
            except Exception as e:
                print(f"\nError: {e}")
            pause()
            
        elif choice == "3":
            print_header("View Attendance Report")
            try:
                enroll_id = int(input("Enrollment ID: "))
                report = attendance_ops.get_attendance_report(conn, enroll_id)
                if report:
                    print(f"\nAttendance history for Enrollment {enroll_id}:")
                    print(f"{'Session Date':<15} {'Status'}")
                    print("-" * 30)
                    for r in report:
                        print(f"{str(r['session_date']):<15} {r['status']}")
                else:
                    print("\nNo attendance records found.")
            except Exception as e:
                print(f"\nError: {e}")
            pause()
            
        elif choice == "0":
            break

def handle_submit_result(conn):
    print_header("Submit Academic Result")
    try:
        enroll_id = int(input("Enrollment ID: "))
        marks = float(input("Marks Obtained: "))
        total = float(input("Total Marks (default 100): ") or 100.0)
        finalized = input("Finalize marks? (y/n, default n): ").lower() == 'y'
        
        res_id = result_ops.submit_result(conn, enroll_id, marks, total, finalized)
        print(f"\nResult successfully saved. Result ID: {res_id}")
        print("Student summary is updated automatically in database.")
    except Exception as e:
        print(f"\nError: {e}")
    pause()

def handle_generate_transcript(conn):
    print_header("Generate Student Transcript")
    try:
        s_id = int(input("Student ID: "))
        summary = transcript_ops.get_student_summary(conn, s_id)
        if not summary:
            print("\nStudent profile not found.")
            pause()
            return
            
        print("\n" + "*" * 60)
        print("UNIVERSITY TRANSCRIPT".center(60))
        print("*" * 60)
        print(f"Name: {summary['first_name']} {summary['last_name']:<30} Roll Number: {summary['roll_number']}")
        print(f"CGPA: {summary['cgpa']:<36} Standing: {summary['academic_standing']}")
        print(f"Total Completed Credits: {summary['total_credit_hours']}")
        print("*" * 60)
        
        records = transcript_ops.generate_transcript(conn, s_id)
        if records:
            current_sem = None
            for r in records:
                if r['semester_name'] != current_sem:
                    current_sem = r['semester_name']
                    print(f"\n--- {current_sem.upper()} (GPA: {r['semester_gpa']}) ---")
                    print(f"{'Course Code':<12} {'Course Name':<30} {'Credits':<8} {'Marks':<8} {'Grade'}")
                    print("-" * 65)
                print(f"{r['course_code']:<12} {r['course_name']:<30} {r['credit_hours']:<8} {r['marks']:<8} {r['grade']}")
        else:
            print("\nNo academic results found. Transcript is empty.")
        print("*" * 60)
    except Exception as e:
        print(f"\nError: {e}")
    pause()

def handle_run_benchmarks():
    print_header("Run DB Query Benchmarks")
    try:
        import benchmark
        benchmark.run_benchmarks()
    except ImportError:
        print("Benchmark script not found or not yet implemented.")
    except Exception as e:
        print(f"Error: {e}")
    pause()

def handle_run_stress_tests():
    print_header("Run DB Stress Tests")
    try:
        import stress_test
        stress_test.run_stress_test()
    except ImportError:
        print("Stress test script not found or not yet implemented.")
    except Exception as e:
        print(f"Error: {e}")
    pause()

def main():
    while True:
        print_header("University Management System")
        print("1. Initialize Database (Drop & Create)")
        print("2. Seed Sample Data (Faker Seeder)")
        print("3. Student CRUD Operations")
        print("4. Teacher & Course Operations")
        print("5. Enroll Student in Course")
        print("6. Attendance Management")
        print("7. Submit Results & Marks")
        print("8. View Student Transcript")
        print("9. Run Query Performance Benchmarks")
        print("10. Run Database Stress Tests")
        print("0. Exit")
        
        choice = input("\nEnter choice: ").strip()
        if choice == "0":
            print("\nGoodbye!")
            sys.exit(0)
            
        elif choice == "1":
            handle_init_db()
            
        elif choice == "2":
            handle_seed_data()
            
        else:
            # For options 3-8, we need a working database connection
            try:
                conn = get_connection()
                if choice == "3":
                    handle_student_ops(conn)
                elif choice == "4":
                    handle_teacher_ops(conn)
                elif choice == "5":
                    handle_enroll_student(conn)
                elif choice == "6":
                    handle_attendance_ops(conn)
                elif choice == "7":
                    handle_submit_result(conn)
                elif choice == "8":
                    handle_generate_transcript(conn)
                elif choice == "9":
                    conn.close() # Benchmark handles its own connection
                    handle_run_benchmarks()
                elif choice == "10":
                    conn.close() # Stress test handles its own connection
                    handle_run_stress_tests()
                else:
                    print("\nInvalid choice! Please select a valid menu option.")
                    pause()
                
                # Check if connection was closed in choices, otherwise close it
                try:
                    if conn and not conn.closed:
                        conn.close()
                except Exception:
                    pass
                    
            except Exception as e:
                print(f"\nDatabase Connection Error: {e}")
                print("Make sure PostgreSQL is running and credentials in config.py are correct.")
                pause()

if __name__ == "__main__":
    main()
