import psycopg2
from psycopg2.extras import execute_values

def mark_attendance(conn, enrollment_id, session_date, status):
    """
    Marks attendance for a single student enrollment on a given date.
    Triggers automatically compute the updated totals and percentages.
    """
    if status not in ('Present', 'Absent', 'Late', 'Excused'):
        raise ValueError("Status must be one of 'Present', 'Absent', 'Late', 'Excused'")
        
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO attendance (enrollment_id, session_date, status)
                VALUES (%s, %s, %s)
                ON CONFLICT (enrollment_id, session_date) 
                DO UPDATE SET status = EXCLUDED.status
                RETURNING attendance_id;
            """, (enrollment_id, session_date, status))
            attendance_id = cur.fetchone()[0]
        conn.commit()
        return attendance_id
    except Exception as e:
        conn.rollback()
        raise e

def mark_bulk_attendance(conn, course_id, semester_id, session_date, attendance_list):
    """
    Marks attendance in bulk for a class session.
    attendance_list: List of tuples (student_id, status)
    Resolves student_id to enrollment_id for the course+semester.
    """
    try:
        with conn.cursor() as cur:
            # Resolve student_id to active enrollment_id for this course and semester
            cur.execute("""
                SELECT student_id, enrollment_id
                FROM enrollment
                WHERE course_id = %s AND semester_id = %s AND status = 'Active';
            """, (course_id, semester_id))
            
            student_to_enrollment = {row[0]: row[1] for row in cur.fetchall()}
            
            # Prepare rows to insert
            records = []
            for student_id, status in attendance_list:
                if status not in ('Present', 'Absent', 'Late', 'Excused'):
                    continue
                if student_id in student_to_enrollment:
                    records.append((student_to_enrollment[student_id], session_date, status))
            
            if not records:
                return False
                
            # Perform batch insert/upsert
            execute_values(
                cur,
                """
                INSERT INTO attendance (enrollment_id, session_date, status)
                VALUES %s
                ON CONFLICT (enrollment_id, session_date) 
                DO UPDATE SET status = EXCLUDED.status;
                """,
                records
            )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e

def get_attendance_report(conn, enrollment_id):
    """Retrieves full attendance records for an enrollment."""
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT session_date, status
                FROM attendance
                WHERE enrollment_id = %s
                ORDER BY session_date DESC;
            """, (enrollment_id,))
            return cur.fetchall()
    except Exception as e:
        conn.rollback()
        raise e
