import time
import psycopg2
from config import get_connection

def get_sample_ids(conn):
    """Dynamically fetches sample IDs from the database to prevent benchmark query misses."""
    with conn.cursor() as cur:
        # Get a student
        cur.execute("SELECT student_id, roll_number, dept_id FROM student LIMIT 1;")
        student = cur.fetchone()
        
        # Get an enrollment
        cur.execute("SELECT enrollment_id, course_id, semester_id FROM enrollment LIMIT 1;")
        enrollment = cur.fetchone()
        
        return {
            "student_id": student[0] if student else 1,
            "roll_number": student[1] if student else '2023-CS-0001',
            "dept_id": student[2] if student else 1,
            "enrollment_id": enrollment[0] if enrollment else 1,
            "course_id": enrollment[1] if enrollment else 1,
            "semester_id": enrollment[2] if enrollment else 1
        }

def run_explain_analyze(cur, query, params=None):
    """Runs EXPLAIN ANALYZE on a query and returns execution time and plan lines."""
    explain_query = f"EXPLAIN (ANALYZE, COSTS ON, TIMING ON) {query}"
    cur.execute(explain_query, params)
    plan = cur.fetchall()
    
    # Extract execution time from plan
    execution_time = 0.0
    plan_lines = []
    for line in plan:
        line_str = line[0]
        plan_lines.append(line_str)
        if "Execution Time:" in line_str:
            # e.g., "Execution Time: 0.125 ms"
            parts = line_str.split(":")
            time_part = parts[1].strip().split(" ")[0]
            execution_time = float(time_part)
            
    return execution_time, "\n".join(plan_lines)

def run_benchmarks():
    print("Connecting to database...")
    try:
        conn = get_connection()
    except Exception as e:
        print(f"Error connecting to DB: {e}")
        return
        
    conn.autocommit = True
    cur = conn.cursor()
    
    # Get IDs
    ids = get_sample_ids(conn)
    print(f"Sample IDs fetched: {ids}")
    
    benchmarks = [
        {
            "name": "Student Profile (Join Dept on Roll Number)",
            "query": "SELECT s.*, d.dept_name FROM student s JOIN department d ON s.dept_id = d.dept_id WHERE s.roll_number = %s",
            "params": (ids["roll_number"],),
            "index_drop": "DROP INDEX IF EXISTS idx_student_dept;",
            "index_create": "CREATE INDEX IF NOT EXISTS idx_student_dept ON student(dept_id);"
        },
        {
            "name": "Semester GPA Computation (Aggregated joins)",
            "query": """
                SELECT COALESCE(SUM(c.credit_hours), 0), COALESCE(SUM(r.grade_points * c.credit_hours), 0)
                FROM result r
                JOIN enrollment e ON r.enrollment_id = e.enrollment_id
                JOIN course c ON e.course_id = c.course_id
                WHERE e.student_id = %s AND e.semester_id = %s
            """,
            "params": (ids["student_id"], ids["semester_id"]),
            "index_drop": "DROP INDEX IF EXISTS idx_enrollment_composite;",
            "index_create": "CREATE INDEX IF NOT EXISTS idx_enrollment_composite ON enrollment(student_id, semester_id);"
        },
        {
            "name": "Materialized Transcript Snapshot Retrieval",
            "query": "SELECT * FROM transcript WHERE student_id = %s AND semester_id = %s",
            "params": (ids["student_id"], ids["semester_id"]),
            "index_drop": "DROP INDEX IF EXISTS idx_transcript_composite;",
            "index_create": "CREATE INDEX IF NOT EXISTS idx_transcript_composite ON transcript(student_id, semester_id);"
        },
        {
            "name": "Attendance Percentage Calculation (Aggregation)",
            "query": "SELECT COUNT(*), COUNT(*) FILTER (WHERE status = 'Present') FROM attendance WHERE enrollment_id = %s",
            "params": (ids["enrollment_id"],),
            "index_drop": "DROP INDEX IF EXISTS idx_attendance_enrollment;",
            "index_create": "CREATE INDEX IF NOT EXISTS idx_attendance_enrollment ON attendance(enrollment_id);"
        },
        {
            "name": "Course Enrollment Count (Aggregated grouping)",
            "query": "SELECT course_id, COUNT(*) FROM enrollment GROUP BY course_id",
            "params": None,
            "index_drop": "DROP INDEX IF EXISTS idx_enrollment_course;",
            "index_create": "CREATE INDEX IF NOT EXISTS idx_enrollment_course ON enrollment(course_id);"
        }
    ]
    
    print("\n" + "="*80)
    print("DATABASE QUERY PERFORMANCE BENCHMARK".center(80))
    print("="*80)
    print(f"{'Benchmark Target':<45} | {'With Index':<12} | {'No Index':<12} | {'Speedup'}")
    print("-"*80)
    
    for b in benchmarks:
        name = b["name"]
        query = b["query"]
        params = b["params"]
        
        # 1. Benchmark with Index
        time_with_idx, plan_with_idx = run_explain_analyze(cur, query, params)
        
        # 2. Drop Index
        cur.execute(b["index_drop"])
        
        # 3. Benchmark without Index
        time_no_idx, plan_no_idx = run_explain_analyze(cur, query, params)
        
        # 4. Recreate Index
        cur.execute(b["index_create"])
        
        # Calculate speedup
        speedup = f"{time_no_idx / max(time_with_idx, 0.001):.1f}x" if time_with_idx > 0 else "N/A"
        
        print(f"{name:<45} | {time_with_idx:>8.3f} ms | {time_no_idx:>8.3f} ms | {speedup:>7}")
        
    print("="*80)
    print("Benchmark run complete. Indexes restored.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    run_benchmarks()
