"""
Flask Web Application for University Management System
Provides a web-based interface for managing students, teachers, courses, etc.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
import psycopg2
import psycopg2.extras
from config import get_connection, DB_CONFIG
from datetime import datetime, date
import traceback

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'university_management_secret_key_2024'
CORS(app)

# Add built-in functions to Jinja2 globals
app.jinja_env.globals.update(max=max, min=min)

# Helper function for database connections
def get_db():
    try:
        return get_connection()
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

# =======================
# DASHBOARD ROUTES
# =======================

@app.route('/')
def index():
    """Main dashboard"""
    conn = get_db()
    if not conn:
        return "Database connection failed", 500
    
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Get statistics
            cur.execute("SELECT COUNT(*) as count FROM student;")
            student_count = cur.fetchone()['count']
            
            cur.execute("SELECT COUNT(*) as count FROM teacher;")
            teacher_count = cur.fetchone()['count']
            
            cur.execute("SELECT COUNT(*) as count FROM course;")
            course_count = cur.fetchone()['count']
            
            cur.execute("SELECT COUNT(*) as count FROM enrollment;")
            enrollment_count = cur.fetchone()['count']
            
            stats = {
                'students': student_count,
                'teachers': teacher_count,
                'courses': course_count,
                'enrollments': enrollment_count
            }
        
        conn.close()
        return render_template('index.html', stats=stats)
    except Exception as e:
        conn.close()
        print(f"Error: {e}")
        return f"Error: {str(e)}", 500

# =======================
# STUDENT ROUTES
# =======================

@app.route('/students')
def students():
    """List all students"""
    conn = get_db()
    if not conn:
        return "Database connection failed", 500
    
    try:
        page = request.args.get('page', 1, type=int)
        limit = 20
        offset = (page - 1) * limit
        
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT s.student_id, s.roll_number, s.first_name, s.last_name, 
                       s.email, s.cgpa, s.academic_standing, d.dept_code
                FROM student s
                JOIN department d ON s.dept_id = d.dept_id
                ORDER BY s.student_id
                LIMIT %s OFFSET %s;
            """, (limit, offset))
            students_list = cur.fetchall()
            
            cur.execute("SELECT COUNT(*) as count FROM student;")
            total = cur.fetchone()['count']
        
        conn.close()
        total_pages = (total + limit - 1) // limit
        return render_template('students_list.html', students=students_list, 
                             page=page, total_pages=total_pages, total=total)
    except Exception as e:
        conn.close()
        print(f"Error: {e}")
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('index'))

@app.route('/student/add', methods=['GET', 'POST'])
def add_student():
    """Add new student"""
    if request.method == 'GET':
        conn = get_db()
        if not conn:
            return "Database connection failed", 500
        
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT dept_id, dept_name FROM department ORDER BY dept_name;")
                departments = cur.fetchall()
            conn.close()
            return render_template('add_student.html', departments=departments)
        except Exception as e:
            conn.close()
            return f"Error: {str(e)}", 500
    
    # POST request
    conn = get_db()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.json
        else:
            data = request.form
        
        dept_id = data.get('dept_id')
        roll_number = data.get('roll_number')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        date_of_birth = data.get('date_of_birth')
        admission_date = data.get('admission_date', date.today().isoformat())
        
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO student 
                (dept_id, roll_number, first_name, last_name, email, date_of_birth, admission_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING student_id;
            """, (dept_id, roll_number, first_name, last_name, email, date_of_birth, admission_date))
            student_id = cur.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        if request.is_json:
            return jsonify({'success': True, 'student_id': student_id})
        else:
            flash(f"Student {first_name} {last_name} added successfully!", "success")
            return redirect(url_for('view_student', student_id=student_id))
    
    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"Error: {e}")
        error_msg = str(e)
        if 'violates unique constraint' in error_msg:
            error_msg = "Roll number or email already exists"
        
        if request.is_json:
            return jsonify({'success': False, 'error': error_msg}), 400
        else:
            flash(f"Error: {error_msg}", "danger")
            return redirect(url_for('add_student'))

@app.route('/student/<int:student_id>')
def view_student(student_id):
    """View student profile and details"""
    conn = get_db()
    if not conn:
        return "Database connection failed", 500
    
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Get student info
            cur.execute("""
                SELECT s.*, d.dept_name, d.dept_code
                FROM student s
                JOIN department d ON s.dept_id = d.dept_id
                WHERE s.student_id = %s;
            """, (student_id,))
            student = cur.fetchone()
            
            if not student:
                conn.close()
                flash("Student not found", "danger")
                return redirect(url_for('students'))
            
            # Get enrollments
            cur.execute("""
                SELECT e.enrollment_id, c.course_id, c.course_name, c.course_code, 
                       c.credit_hours AS credits, e.enrollment_date
                FROM enrollment e
                JOIN course c ON e.course_id = c.course_id
                WHERE e.student_id = %s
                ORDER BY e.enrollment_date DESC;
            """, (student_id,))
            enrollments = cur.fetchall()
            
            # Get results
            cur.execute("""
                  SELECT r.result_id,
                      c.course_code,
                      c.course_name,
                      c.credit_hours AS credits,
                      r.marks_obtained AS marks,
                      COALESCE(gs.letter_grade, '') AS grade,
                      COALESCE(r.grade_points, gs.grade_point, 0) AS gpa_points
                  FROM result r
                  JOIN enrollment e ON r.enrollment_id = e.enrollment_id
                  JOIN course c ON e.course_id = c.course_id
                  LEFT JOIN grade_scale gs ON r.grade_id = gs.grade_id
                  WHERE e.student_id = %s
                  ORDER BY c.course_code;
            """, (student_id,))
            results = cur.fetchall()
            
            # Get attendance
            cur.execute("""
                  SELECT c.course_code,
                      c.course_name,
                      COUNT(CASE WHEN a.status = 'Present' THEN 1 END) as present,
                      COUNT(a.attendance_id) as total
                  FROM attendance a
                  JOIN enrollment e ON a.enrollment_id = e.enrollment_id
                  JOIN course c ON e.course_id = c.course_id
                  WHERE e.student_id = %s
                GROUP BY c.course_id, c.course_code, c.course_name;
            """, (student_id,))
            attendance_summary = cur.fetchall()
        
        conn.close()
        return render_template('student_profile.html', student=student, 
                             enrollments=enrollments, results=results, 
                             attendance_summary=attendance_summary)
    except Exception as e:
        conn.close()
        print(f"Error: {e}")
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('students'))

@app.route('/student/<int:student_id>/edit', methods=['GET', 'POST'])
def edit_student(student_id):
    """Edit student information"""
    conn = get_db()
    if not conn:
        return "Database connection failed", 500
    
    if request.method == 'GET':
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT * FROM student WHERE student_id = %s;", (student_id,))
                student = cur.fetchone()
                
                cur.execute("SELECT dept_id, dept_name FROM department ORDER BY dept_name;")
                departments = cur.fetchall()
            
            conn.close()
            if not student:
                flash("Student not found", "danger")
                return redirect(url_for('students'))
            
            return render_template('edit_student.html', student=student, departments=departments)
        except Exception as e:
            conn.close()
            flash(f"Error: {str(e)}", "danger")
            return redirect(url_for('students'))
    
    # POST request
    try:
        data = request.form
        dept_id = data.get('dept_id')
        roll_number = data.get('roll_number')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE student 
                SET dept_id = %s, roll_number = %s, first_name = %s, 
                    last_name = %s, email = %s
                WHERE student_id = %s;
            """, (dept_id, roll_number, first_name, last_name, email, student_id))
        
        conn.commit()
        conn.close()
        
        flash("Student information updated successfully!", "success")
        return redirect(url_for('view_student', student_id=student_id))
    except Exception as e:
        conn.rollback()
        conn.close()
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('edit_student', student_id=student_id))

# =======================
# TEACHER ROUTES
# =======================

@app.route('/teachers')
def teachers():
    """List all teachers"""
    conn = get_db()
    if not conn:
        return "Database connection failed", 500
    
    try:
        page = request.args.get('page', 1, type=int)
        limit = 20
        offset = (page - 1) * limit
        
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT t.teacher_id, t.first_name, t.last_name, t.email, 
                       t.designation, t.hire_date, d.dept_code
                FROM teacher t
                JOIN department d ON t.dept_id = d.dept_id
                ORDER BY t.teacher_id
                LIMIT %s OFFSET %s;
            """, (limit, offset))
            teachers_list = cur.fetchall()
            
            cur.execute("SELECT COUNT(*) as count FROM teacher;")
            total = cur.fetchone()['count']
        
        conn.close()
        total_pages = (total + limit - 1) // limit
        return render_template('teachers_list.html', teachers=teachers_list, 
                             page=page, total_pages=total_pages, total=total)
    except Exception as e:
        conn.close()
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('index'))

@app.route('/teacher/add', methods=['GET', 'POST'])
def add_teacher():
    """Add new teacher"""
    if request.method == 'GET':
        conn = get_db()
        if not conn:
            return "Database connection failed", 500
        
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT dept_id, dept_name FROM department ORDER BY dept_name;")
                departments = cur.fetchall()
            conn.close()
            return render_template('add_teacher.html', departments=departments)
        except Exception as e:
            conn.close()
            return f"Error: {str(e)}", 500
    
    # POST request
    conn = get_db()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    try:
        data = request.get_json(silent=True) or request.form
        dept_id = data.get('dept_id')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        hire_date = data.get('hire_date', date.today().isoformat())
        designation = data.get('designation')
        
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO teacher 
                (dept_id, first_name, last_name, email, hire_date, designation)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING teacher_id;
            """, (dept_id, first_name, last_name, email, hire_date, designation))
            teacher_id = cur.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        if request.is_json:
            return jsonify({'success': True, 'teacher_id': teacher_id})
        else:
            flash(f"Teacher {first_name} {last_name} added successfully!", "success")
            return redirect(url_for('view_teacher', teacher_id=teacher_id))
    
    except Exception as e:
        conn.rollback()
        conn.close()
        error_msg = str(e)
        if 'violates unique constraint' in error_msg:
            error_msg = "Email already exists"
        
        if request.is_json:
            return jsonify({'success': False, 'error': error_msg}), 400
        else:
            flash(f"Error: {error_msg}", "danger")
            return redirect(url_for('add_teacher'))

@app.route('/teacher/<int:teacher_id>')
def view_teacher(teacher_id):
    """View teacher profile"""
    conn = get_db()
    if not conn:
        return "Database connection failed", 500
    
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Get teacher info
            cur.execute("""
                SELECT t.*, d.dept_name, d.dept_code
                FROM teacher t
                JOIN department d ON t.dept_id = d.dept_id
                WHERE t.teacher_id = %s;
            """, (teacher_id,))
            teacher = cur.fetchone()
            
            if not teacher:
                conn.close()
                flash("Teacher not found", "danger")
                return redirect(url_for('teachers'))
            
            # Get assigned courses
            cur.execute("""
                SELECT course_id, course_code, course_name, credit_hours AS credits
                FROM course
                WHERE teacher_id = %s
                ORDER BY course_name;
            """, (teacher_id,))
            courses = cur.fetchall()
        
        conn.close()
        return render_template('teacher_profile.html', teacher=teacher, courses=courses)
    except Exception as e:
        conn.close()
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('teachers'))

# =======================
# COURSE ROUTES
# =======================

@app.route('/courses')
def courses():
    """List all courses"""
    conn = get_db()
    if not conn:
        return "Database connection failed", 500
    
    try:
        page = request.args.get('page', 1, type=int)
        limit = 20
        offset = (page - 1) * limit
        
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT c.course_id, c.course_code, c.course_name, c.credit_hours AS credits, 
                       d.dept_code, CONCAT(t.first_name, ' ', t.last_name) as teacher_name,
                       COUNT(e.enrollment_id) as enrollment_count
                FROM course c
                JOIN department d ON c.dept_id = d.dept_id
                LEFT JOIN teacher t ON c.teacher_id = t.teacher_id
                LEFT JOIN enrollment e ON c.course_id = e.course_id
                GROUP BY c.course_id, d.dept_code, t.first_name, t.last_name
                ORDER BY c.course_code
                LIMIT %s OFFSET %s;
            """, (limit, offset))
            courses_list = cur.fetchall()
            
            cur.execute("SELECT COUNT(*) as count FROM course;")
            total = cur.fetchone()['count']
        
        conn.close()
        total_pages = (total + limit - 1) // limit
        return render_template('courses_list.html', courses=courses_list, 
                             page=page, total_pages=total_pages, total=total)
    except Exception as e:
        conn.close()
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('index'))

@app.route('/course/add', methods=['GET', 'POST'])
def add_course():
    """Add new course"""
    if request.method == 'GET':
        conn = get_db()
        if not conn:
            return "Database connection failed", 500
        
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT dept_id, dept_name FROM department ORDER BY dept_name;")
                departments = cur.fetchall()
                
                cur.execute("SELECT teacher_id, first_name, last_name FROM teacher ORDER BY first_name;")
                teachers = cur.fetchall()
            conn.close()
            return render_template('add_course.html', departments=departments, teachers=teachers)
        except Exception as e:
            conn.close()
            return f"Error: {str(e)}", 500
    
    # POST request
    conn = get_db()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    try:
        data = request.get_json(silent=True) or request.form
        dept_id = data.get('dept_id')
        course_code = data.get('course_code')
        course_name = data.get('course_name')
        credits = int(data.get('credits', 3))
        teacher_id = data.get('teacher_id') or None
        
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO course 
                (dept_id, course_code, course_name, credit_hours, teacher_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING course_id;
            """, (dept_id, course_code, course_name, credits, teacher_id if teacher_id else None))
            course_id = cur.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        if request.is_json:
            return jsonify({'success': True, 'course_id': course_id})
        else:
            flash(f"Course {course_name} added successfully!", "success")
            return redirect(url_for('view_course', course_id=course_id))
    
    except Exception as e:
        conn.rollback()
        conn.close()
        error_msg = str(e)
        if request.is_json:
            return jsonify({'success': False, 'error': error_msg}), 400
        else:
            flash(f"Error: {error_msg}", "danger")
            return redirect(url_for('add_course'))

@app.route('/course/<int:course_id>')
def view_course(course_id):
    """View course details"""
    conn = get_db()
    if not conn:
        return "Database connection failed", 500
    
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Get course info
            cur.execute("""
                SELECT c.course_id, c.dept_id, c.teacher_id, c.course_code, c.course_name,
                       c.credit_hours AS credits, c.max_capacity, c.current_enrollment,
                       d.dept_name, CONCAT(t.first_name, ' ', t.last_name) as teacher_name
                FROM course c
                JOIN department d ON c.dept_id = d.dept_id
                LEFT JOIN teacher t ON c.teacher_id = t.teacher_id
                WHERE c.course_id = %s;
            """, (course_id,))
            course = cur.fetchone()
            
            if not course:
                conn.close()
                flash("Course not found", "danger")
                return redirect(url_for('courses'))
            
            # Get enrolled students
            cur.execute("""
                SELECT e.enrollment_id, s.student_id, s.roll_number, 
                       s.first_name, s.last_name, e.enrollment_date
                FROM enrollment e
                JOIN student s ON e.student_id = s.student_id
                WHERE e.course_id = %s
                ORDER BY s.roll_number;
            """, (course_id,))
            students = cur.fetchall()
        
        conn.close()
        return render_template('course_profile.html', course=course, students=students)
    except Exception as e:
        conn.close()
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('courses'))

# =======================
# ENROLLMENT ROUTES
# =======================

@app.route('/enrollments')
def enrollments():
    """List all enrollments"""
    conn = get_db()
    if not conn:
        return "Database connection failed", 500
    
    try:
        page = request.args.get('page', 1, type=int)
        limit = 20
        offset = (page - 1) * limit
        
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT e.enrollment_id, s.student_id, CONCAT(s.first_name, ' ', s.last_name) as student_name,
                       c.course_id, c.course_code, c.course_name, e.enrollment_date
                FROM enrollment e
                JOIN student s ON e.student_id = s.student_id
                JOIN course c ON e.course_id = c.course_id
                ORDER BY e.enrollment_date DESC
                LIMIT %s OFFSET %s;
            """, (limit, offset))
            enrollments_list = cur.fetchall()
            
            cur.execute("SELECT COUNT(*) as count FROM enrollment;")
            total = cur.fetchone()['count']
        
        conn.close()
        total_pages = (total + limit - 1) // limit
        return render_template('enrollments_list.html', enrollments=enrollments_list, 
                             page=page, total_pages=total_pages, total=total)
    except Exception as e:
        conn.close()
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('index'))

@app.route('/enrollment/add', methods=['GET', 'POST'])
def add_enrollment():
    """Add new enrollment (enroll student in course)"""
    if request.method == 'GET':
        conn = get_db()
        if not conn:
            return "Database connection failed", 500
        
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT s.student_id, CONCAT(s.first_name, ' ', s.last_name) as student_name, s.roll_number
                    FROM student s
                    ORDER BY s.first_name;
                """)
                students = cur.fetchall()
                
                cur.execute("""
                    SELECT c.course_id, CONCAT(c.course_code, ' - ', c.course_name) as course_name
                    FROM course c
                    ORDER BY c.course_code;
                """)
                courses = cur.fetchall()
            
            conn.close()
            return render_template('add_enrollment.html', students=students, courses=courses)
        except Exception as e:
            conn.close()
            return f"Error: {str(e)}", 500
    
    # POST request
    conn = get_db()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    try:
        data = request.json or request.form
        student_id = data.get('student_id')
        course_id = data.get('course_id')
        enrollment_date = data.get('enrollment_date', date.today().isoformat())
        
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO enrollment (student_id, course_id, enrollment_date)
                VALUES (%s, %s, %s)
                RETURNING enrollment_id;
            """, (student_id, course_id, enrollment_date))
            enrollment_id = cur.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': True, 'enrollment_id': enrollment_id})
        else:
            flash("Student enrolled successfully!", "success")
            return redirect(url_for('enrollments'))
    
    except Exception as e:
        conn.rollback()
        conn.close()
        error_msg = str(e)
        if 'duplicate key' in error_msg:
            error_msg = "Student is already enrolled in this course"
        
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': False, 'error': error_msg}), 400
        else:
            flash(f"Error: {error_msg}", "danger")
            return redirect(url_for('add_enrollment'))

@app.route('/enrollment/<int:enrollment_id>/drop', methods=['POST'])
def drop_enrollment(enrollment_id):
    """Drop a course enrollment"""
    conn = get_db()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM enrollment WHERE enrollment_id = %s;", (enrollment_id,))
        
        conn.commit()
        conn.close()
        
        flash("Enrollment dropped successfully!", "success")
        return redirect(request.referrer or url_for('enrollments'))
    except Exception as e:
        conn.rollback()
        conn.close()
        flash(f"Error: {str(e)}", "danger")
        return redirect(request.referrer or url_for('enrollments'))

# =======================
# ATTENDANCE ROUTES
# =======================

@app.route('/attendance')
def attendance():
    """Attendance management"""
    conn = get_db()
    if not conn:
        return "Database connection failed", 500
    conn.close()
    return render_template('attendance.html')

@app.route('/attendance/mark', methods=['POST'])
def mark_attendance():
    """Mark attendance for a student"""
    conn = get_db()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    try:
        data = request.get_json(silent=True) or request.form
        roll_number = data.get('roll_number')
        course_id = data.get('course_id')
        attendance_date = data.get('attendance_date')
        status = data.get('status')
        
        with conn.cursor() as cur:
            cur.execute("""
                SELECT student_id
                FROM student
                WHERE roll_number = %s;
            """, (roll_number,))
            student_row = cur.fetchone()

            if not student_row:
                conn.close()
                flash("Student roll number not found.", "danger")
                return redirect(request.referrer or url_for('attendance'))

            student_id = student_row[0]

            cur.execute("""
                SELECT enrollment_id
                FROM enrollment
                WHERE student_id = %s AND course_id = %s;
            """, (student_id, course_id))
            enrollment_row = cur.fetchone()

            if not enrollment_row:
                conn.close()
                flash("Enrollment not found for the selected student and course.", "danger")
                return redirect(request.referrer or url_for('attendance'))

            enrollment_id = enrollment_row[0]

            cur.execute("""
                INSERT INTO attendance (enrollment_id, session_date, status)
                VALUES (%s, %s, %s)
                ON CONFLICT (enrollment_id, session_date) 
                DO UPDATE SET status = %s;
            """, (enrollment_id, attendance_date, status, status))
        
        conn.commit()
        conn.close()
        
        flash("Attendance marked successfully!", "success")
        return redirect(request.referrer or url_for('attendance'))
    except Exception as e:
        conn.rollback()
        conn.close()
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('attendance'))

@app.route('/student/<int:student_id>/attendance')
def view_attendance(student_id):
    """View attendance records for a student"""
    conn = get_db()
    if not conn:
        return "Database connection failed", 500
    
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM student WHERE student_id = %s;", (student_id,))
            student = cur.fetchone()
            
            if not student:
                conn.close()
                flash("Student not found", "danger")
                return redirect(url_for('students'))
            
            cur.execute("""
                SELECT a.attendance_id,
                       a.session_date AS attendance_date,
                       a.status,
                       c.course_code,
                       c.course_name
                FROM attendance a
                JOIN enrollment e ON a.enrollment_id = e.enrollment_id
                JOIN course c ON e.course_id = c.course_id
                WHERE e.student_id = %s
                ORDER BY a.session_date DESC;
            """, (student_id,))
            records = cur.fetchall()
        
        conn.close()
        return render_template('attendance_records.html', student=student, records=records)
    except Exception as e:
        conn.close()
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('students'))

# =======================
# RESULT ROUTES
# =======================

@app.route('/results')
def results():
    """Results management"""
    return render_template('results.html')

@app.route('/result/submit', methods=['POST'])
def submit_result():
    """Submit grades for a student"""
    conn = get_db()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    try:
        data = request.get_json(silent=True) or request.form
        student_id = data.get('student_id')
        course_id = data.get('course_id')
        marks = float(data.get('marks'))
        grade = data.get('grade')
        
        with conn.cursor() as cur:
            cur.execute("""
                SELECT enrollment_id
                FROM enrollment
                WHERE student_id = %s AND course_id = %s;
            """, (student_id, course_id))
            enrollment_row = cur.fetchone()

            if not enrollment_row:
                conn.close()
                flash("Enrollment not found for the selected student and course.", "danger")
                return redirect(request.referrer or url_for('results'))

            enrollment_id = enrollment_row[0]

            cur.execute("""
                SELECT grade_id, grade_point
                FROM grade_scale
                WHERE letter_grade = %s;
            """, (grade,))
            grade_row = cur.fetchone()
            grade_id = grade_row[0] if grade_row else None
            grade_points = grade_row[1] if grade_row else None

            cur.execute("""
                INSERT INTO result (enrollment_id, marks_obtained, total_marks, grade_id, grade_points)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (enrollment_id)
                DO UPDATE SET
                    marks_obtained = EXCLUDED.marks_obtained,
                    total_marks = EXCLUDED.total_marks,
                    grade_id = EXCLUDED.grade_id,
                    grade_points = EXCLUDED.grade_points,
                    is_finalized = FALSE;
            """, (enrollment_id, marks, 100, grade_id, grade_points))
        
        conn.commit()
        conn.close()
        
        flash("Grade submitted successfully!", "success")
        return redirect(request.referrer or url_for('results'))
    except Exception as e:
        conn.rollback()
        conn.close()
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('results'))

@app.route('/student/<int:student_id>/results')
def view_student_results(student_id):
    """View results for a student"""
    conn = get_db()
    if not conn:
        return "Database connection failed", 500
    
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM student WHERE student_id = %s;", (student_id,))
            student = cur.fetchone()
            
            if not student:
                conn.close()
                flash("Student not found", "danger")
                return redirect(url_for('students'))
            
            cur.execute("""
                SELECT r.result_id,
                       c.course_code,
                       c.course_name,
                       c.credit_hours AS credits,
                       r.marks_obtained AS marks,
                       COALESCE(gs.letter_grade, '') AS grade,
                       COALESCE(r.grade_points, gs.grade_point, 0) AS gpa_points
                FROM result r
                JOIN enrollment e ON r.enrollment_id = e.enrollment_id
                JOIN course c ON e.course_id = c.course_id
                LEFT JOIN grade_scale gs ON r.grade_id = gs.grade_id
                WHERE e.student_id = %s
                ORDER BY c.course_code;
            """, (student_id,))
            results = cur.fetchall()
        
        conn.close()
        return render_template('student_results.html', student=student, results=results)
    except Exception as e:
        conn.close()
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('students'))

# =======================
# API ENDPOINTS
# =======================

@app.route('/api/students/<int:student_id>/courses', methods=['GET'])
def api_student_courses(student_id):
    """API: Get courses for a student"""
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT c.course_id, c.course_code, c.course_name
                FROM enrollment e
                JOIN course c ON e.course_id = c.course_id
                WHERE e.student_id = %s
                ORDER BY c.course_code;
            """, (student_id,))
            courses = cur.fetchall()
        
        conn.close()
        return jsonify(courses)
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/student-courses', methods=['GET'])
def api_student_courses_by_roll():
    """API: Get courses for a student by roll number"""
    roll_number = request.args.get('roll_number', '').strip()

    if not roll_number:
        return jsonify([])

    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT c.course_id, c.course_code, c.course_name
                FROM student s
                JOIN enrollment e ON s.student_id = e.student_id
                JOIN course c ON e.course_id = c.course_id
                WHERE s.roll_number = %s
                ORDER BY c.course_code;
            """, (roll_number,))
            courses = cur.fetchall()

        conn.close()
        return jsonify(courses)
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/courses', methods=['GET'])
def api_courses():
    """API: Get all courses"""
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT course_id, course_code, course_name
                FROM course
                ORDER BY course_code;
            """)
            courses = cur.fetchall()
        
        conn.close()
        return jsonify(courses)
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

# =======================
# ERROR HANDLERS
# =======================

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
