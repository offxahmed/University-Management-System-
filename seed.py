import random
import datetime
from faker import Faker
import psycopg2
from psycopg2.extras import execute_values
from config import get_connection

fake = Faker()

# Predefined departments
DEPARTMENTS = [
    ("Computer Science", "CS", "Dr. Ayesha Khan"),
    ("Electrical Engineering", "EE", "Dr. Tariq Mahmood"),
    ("Mechanical Engineering", "ME", "Dr. Salman Ahmed"),
    ("Civil Engineering", "CE", "Dr. Zafar Iqbal"),
    ("Chemical Engineering", "CH", "Dr. Maryam Bibi"),
    ("Mathematics", "MATH", "Dr. Asim Raza"),
    ("Physics", "PHYS", "Dr. Haris Jamil"),
    ("Chemistry", "CHEM", "Dr. Sadaf Riaz"),
    ("Biology", "BIOL", "Dr. Noreen Anwar"),
    ("Environmental Sciences", "ENV", "Dr. Bilal Hassan"),
    ("Economics", "ECON", "Dr. Khalid Malik"),
    ("Business Administration", "BA", "Dr. Farhan Ali"),
    ("English Literature", "ENGL", "Dr. Shazia Rehman"),
    ("History", "HIST", "Dr. Usman Yousaf"),
    ("Sociology", "SOCI", "Dr. Nadia Bashir"),
    ("Psychology", "PSYC", "Dr. Fouzia Yasmin"),
    ("Political Science", "POL", "Dr. Imran Sajid"),
    ("Philosophy", "PHIL", "Dr. Adnan Qureshi"),
    ("Statistics", "STAT", "Dr. Mubashar Hussain"),
    ("Art & Design", "ART", "Dr. Zainab Kamal")
]

# Standard letter grade mapping
GRADE_SCALE = [
    ("A+", 90.00, 100.00, 4.00),
    ("A",  85.00, 89.99,  4.00),
    ("A-", 80.00, 84.99,  3.70),
    ("B+", 75.00, 79.99,  3.30),
    ("B",  70.00, 74.99,  3.00),
    ("B-", 65.00, 69.99,  2.70),
    ("C+", 60.00, 64.99,  2.30),
    ("C",  55.00, 59.99,  2.00),
    ("C-", 50.00, 54.99,  1.70),
    ("D",  40.00, 49.99,  1.00),
    ("F",  0.00,  39.99,  0.00)
]

# Semesters (Fall / Spring 2022 to 2025)
SEMESTERS = [
    ("Fall 2022",   datetime.date(2022, 9, 1),   datetime.date(2023, 1, 31), False),
    ("Spring 2023", datetime.date(2023, 2, 15),  datetime.date(2023, 6, 30), False),
    ("Fall 2023",   datetime.date(2023, 9, 1),   datetime.date(2024, 1, 31), False),
    ("Spring 2024", datetime.date(2024, 2, 15),  datetime.date(2024, 6, 30), False),
    ("Fall 2024",   datetime.date(2024, 9, 1),   datetime.date(2025, 1, 31), False),
    ("Spring 2025", datetime.date(2025, 2, 15),  datetime.date(2025, 6, 30), False),
    ("Fall 2025",   datetime.date(2025, 9, 1),   datetime.date(2026, 1, 31), False),
    ("Spring 2026", datetime.date(2026, 2, 15),  datetime.date(2026, 6, 30), True) # Active
]

def seed_departments(conn):
    print("Seeding departments...")
    with conn.cursor() as cur:
        execute_values(
            cur,
            "INSERT INTO department (dept_name, dept_code, hod_name) VALUES %s ON CONFLICT DO NOTHING;",
            DEPARTMENTS
        )
        cur.execute("SELECT dept_id, dept_code FROM department;")
        depts = cur.fetchall()
    conn.commit()
    return depts

def seed_grade_scale(conn):
    print("Seeding grade scale...")
    with conn.cursor() as cur:
        execute_values(
            cur,
            "INSERT INTO grade_scale (letter_grade, min_marks, max_marks, grade_point) VALUES %s ON CONFLICT DO NOTHING;",
            GRADE_SCALE
        )
    conn.commit()

def seed_semesters(conn):
    print("Seeding semesters...")
    with conn.cursor() as cur:
        execute_values(
            cur,
            "INSERT INTO semester (semester_name, start_date, end_date, is_active) VALUES %s ON CONFLICT DO NOTHING;",
            SEMESTERS
        )
        cur.execute("SELECT semester_id, is_active FROM semester;")
        semesters = cur.fetchall()
    conn.commit()
    return semesters

def seed_teachers(conn, depts, count=500):
    print(f"Seeding {count} teachers...")
    teachers_data = []
    designations = ["Lecturer", "Assistant Professor", "Associate Professor", "Professor"]
    
    # Distribute teachers evenly across departments
    teachers_per_dept = count // len(depts)
    
    for dept_id, dept_code in depts:
        for _ in range(teachers_per_dept):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}@{dept_code.lower()}.university.edu"
            hire_date = fake.date_between(start_date="-10y", end_date="-1y")
            designation = random.choice(designations)
            teachers_data.append((dept_id, first_name, last_name, email, hire_date, designation))
            
    # Insert in batch
    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO teacher (dept_id, first_name, last_name, email, hire_date, designation)
            VALUES %s
            ON CONFLICT (email) DO UPDATE SET designation = EXCLUDED.designation;
            """,
            teachers_data
        )
        cur.execute("SELECT teacher_id, dept_id FROM teacher;")
        teachers = cur.fetchall()
    conn.commit()
    return teachers

def seed_courses(conn, depts, teachers, count=300):
    print(f"Seeding {count} courses...")
    courses_data = []
    courses_per_dept = count // len(depts)
    
    # Map teachers to departments for proper assignment
    dept_teachers = {}
    for teacher_id, dept_id in teachers:
        dept_teachers.setdefault(dept_id, []).append(teacher_id)
        
    course_templates = [
        ("Programming Fundamentals", "101"),
        ("Object Oriented Programming", "102"),
        ("Data Structures", "201"),
        ("Database Systems", "301"),
        ("Software Engineering", "302"),
        ("Artificial Intelligence", "401"),
        ("Computer Networks", "303"),
        ("Operating Systems", "304"),
        ("Calculus I", "111"),
        ("Calculus II", "112"),
        ("Linear Algebra", "211"),
        ("Differential Equations", "212"),
        ("Numerical Analysis", "311"),
        ("Probability & Statistics", "213"),
        ("University Physics", "121")
    ]
    
    for dept_id, dept_code in depts:
        assigned_teachers = dept_teachers.get(dept_id, [None])
        for i in range(courses_per_dept):
            # Select course name from template or generate one
            if i < len(course_templates):
                c_name, c_num = course_templates[i]
            else:
                c_name = f"Special Topics in {dept_code} {i}"
                c_num = str(400 + i)
                
            course_code = f"{dept_code}-{c_num}"
            course_name = f"{dept_code} {c_name}" if i >= len(course_templates) else c_name
            credit_hours = random.choice([3, 4])
            max_capacity = random.randint(1000, 1500)  # High capacity to avoid seeding errors
            teacher_id = random.choice(assigned_teachers)
            
            courses_data.append((dept_id, teacher_id, course_code, course_name, credit_hours, max_capacity))
            
    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO course (dept_id, teacher_id, course_code, course_name, credit_hours, max_capacity)
            VALUES %s
            ON CONFLICT (course_code) DO UPDATE SET course_name = EXCLUDED.course_name;
            """,
            courses_data
        )
        cur.execute("SELECT course_id, dept_id FROM course;")
        courses = cur.fetchall()
    conn.commit()
    return courses

def seed_students(conn, depts, count=10000):
    print(f"Seeding {count} students...")
    students_data = []
    students_per_dept = count // len(depts)
    
    # Determine base year for roll numbers
    years = [2022, 2023, 2024, 2025]
    
    for dept_id, dept_code in depts:
        for i in range(students_per_dept):
            year = random.choice(years)
            roll_number = f"{year}-{dept_code}-{i+1:04d}"
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}{i}@{dept_code.lower()}.university.edu"
            dob = fake.date_of_birth(minimum_age=18, maximum_age=25)
            admission_date = datetime.date(year, 9, 1)
            
            students_data.append((dept_id, roll_number, first_name, last_name, email, dob, admission_date))
            
    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO student (dept_id, roll_number, first_name, last_name, email, date_of_birth, admission_date)
            VALUES %s
            ON CONFLICT (roll_number) DO NOTHING;
            """,
            students_data
        )
        cur.execute("SELECT student_id, dept_id FROM student;")
        students = cur.fetchall()
    conn.commit()
    return students

def seed_enrollments_and_results(conn, students, courses, semesters, total_enrollments=100000):
    print(f"Seeding {total_enrollments} enrollments & results...")
    
    # Map courses and students by department
    dept_courses = {}
    for course_id, dept_id in courses:
        dept_courses.setdefault(dept_id, []).append(course_id)
        
    dept_students = {}
    for student_id, dept_id in students:
        dept_students.setdefault(dept_id, []).append(student_id)
        
    semester_ids = [sem[0] for sem in semesters]
    active_semester_id = [sem[0] for sem in semesters if sem[1]][0]
    
    enrollment_records = []
    # Track course capacity globally to avoid trigger exceptions (since trigger is per course, not course+semester)
    course_global_counts = {}
    
    # Generate enrollments
    # For speed and reality: loop through students and enroll them in 4 courses per semester
    enrollments_count = 0
    print("Generating registration plans...")
    
    # Randomly select students to enroll across semesters
    for student_id, dept_id in students:
        if enrollments_count >= total_enrollments:
            break
            
        # Get courses available in student's department + general courses
        avail_courses = dept_courses.get(dept_id, [])
        if not avail_courses:
            continue
            
        # Register student in 3-5 courses for random semesters
        student_semesters = random.sample(semester_ids, k=random.randint(4, 8))
        for sem_id in student_semesters:
            sem_courses = random.sample(avail_courses, k=min(len(avail_courses), random.randint(3, 4)))
            for course_id in sem_courses:
                # Check capacity limit tracker in Python (global count per course)
                current_cnt = course_global_counts.get(course_id, 0)
                if current_cnt >= 450: # Stay safe under maximum capacity (which is at least 1000)
                    continue
                    
                course_global_counts[course_id] = current_cnt + 1
                enrollment_records.append((student_id, course_id, sem_id, datetime.date.today(), 'Active'))
                enrollments_count += 1
                
    # Batch insert enrollments
    print(f"Inserting {len(enrollment_records)} enrollments...")
    
    # We slice it to prevent large SQL memory issue
    batch_size = 10000
    with conn.cursor() as cur:
        for i in range(0, len(enrollment_records), batch_size):
            batch = enrollment_records[i:i+batch_size]
            execute_values(
                cur,
                """
                INSERT INTO enrollment (student_id, course_id, semester_id, enrollment_date, status)
                VALUES %s
                ON CONFLICT (student_id, course_id, semester_id) DO NOTHING;
                """,
                batch
            )
        conn.commit()
        
    # Query all inserted enrollments to get full list of IDs
    with conn.cursor() as cur:
        cur.execute("SELECT enrollment_id, semester_id FROM enrollment;")
        enrollments_inserted = cur.fetchall()
    print(f"Successfully enrolled {len(enrollments_inserted)} records.")
    
    # Now generate and insert results for completed semesters
    print("Generating and inserting academic results...")
    result_records = []
    for enroll_id, sem_id in enrollments_inserted:
        # If it is NOT the active semester, we submit results
        if sem_id != active_semester_id:
            marks = round(random.uniform(35.0, 98.0), 2) # Random grade marks
            result_records.append((enroll_id, marks, 100.0, True))
            
    print(f"Inserting {len(result_records)} result rows (this will trigger GPA, CGPA & transcripts calculations)...")
    # Batch insert results
    with conn.cursor() as cur:
        for i in range(0, len(result_records), batch_size):
            batch = result_records[i:i+batch_size]
            execute_values(
                cur,
                """
                INSERT INTO result (enrollment_id, marks_obtained, total_marks, is_finalized)
                VALUES %s
                ON CONFLICT (enrollment_id) DO NOTHING;
                """,
                batch
            )
            print(f"Inserted {min(i+batch_size, len(result_records))}/{len(result_records)} results...")
        conn.commit()
    print("Results and cascading computations complete.")

def seed_all():
    print("=== SEEDING DATABASE ===")
    start_time = datetime.datetime.now()
    conn = get_connection()
    try:
        depts = seed_departments(conn)
        seed_grade_scale(conn)
        semesters = seed_semesters(conn)
        teachers = seed_teachers(conn, depts, count=500)
        courses = seed_courses(conn, depts, teachers, count=300)
        students = seed_students(conn, depts, count=10000)
        seed_enrollments_and_results(conn, students, courses, semesters, total_enrollments=100000)
        
        end_time = datetime.datetime.now()
        duration = end_time - start_time
        print(f"=== SEEDING COMPLETED SUCCESSFULY in {duration.total_seconds():.2f} seconds ===")
    except Exception as e:
        print(f"Error during seeding: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    seed_all()
