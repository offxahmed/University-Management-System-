import time
import random
import datetime
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
import psycopg2
from psycopg2.extras import execute_values
from config import get_connection
from operations import enrollment_ops, attendance_ops, result_ops

def get_db_records(conn):
    """Fetches sample datasets from database to feed the simulation."""
    with conn.cursor() as cur:
        # Get active student IDs
        cur.execute("SELECT student_id, dept_id FROM student LIMIT 1000;")
        students = cur.fetchall()
        
        # Get course IDs
        cur.execute("SELECT course_id, dept_id FROM course LIMIT 500;")
        courses = cur.fetchall()
        
        # Get active semester IDs
        cur.execute("SELECT semester_id FROM semester WHERE is_active = TRUE LIMIT 1;")
        active_semester = cur.fetchone()
        
        # Get active enrollment IDs
        cur.execute("SELECT enrollment_id, student_id, course_id FROM enrollment LIMIT 5000;")
        enrollments = cur.fetchall()
        
    return {
        "students": students,
        "courses": courses,
        "active_semester_id": active_semester[0] if active_semester else 1,
        "enrollments": enrollments
    }

def run_bulk_insert_test(conn, num_records=100000):
    """
    Simulates high-volume insert pressure on the attendance table.
    Measues bulk ingestion throughput under trigger calculation load.
    """
    print(f"\n--- Running Bulk Ingestion Test ({num_records} rows) ---")
    with conn.cursor() as cur:
        # Fetch enrollment IDs to reference
        cur.execute("SELECT enrollment_id FROM enrollment LIMIT 20000;")
        enrollment_ids = [row[0] for row in cur.fetchall()]
        
    if not enrollment_ids:
        print("No enrollments found. Please seed the database first.")
        return
        
    print(f"Generating {num_records} attendance records...")
    statuses = ["Present", "Absent", "Late", "Excused"]
    base_date = datetime.date.today()
    
    # Pre-generate tuples in memory
    records = []
    for i in range(num_records):
        enroll_id = random.choice(enrollment_ids)
        # Random date within the last 180 days
        session_date = base_date - datetime.timedelta(days=random.randint(0, 180))
        status = random.choice(statuses)
        records.append((enroll_id, session_date, status))
        
    print(f"Ingesting into DB in chunks of 10,000 rows (triggers are firing)...")
    start_time = time.time()
    
    chunk_size = 10000
    with conn.cursor() as cur:
        for offset in range(0, num_records, chunk_size):
            chunk = records[offset : offset + chunk_size]
            execute_values(
                cur,
                """
                INSERT INTO attendance (enrollment_id, session_date, status)
                VALUES %s
                ON CONFLICT (enrollment_id, session_date) DO UPDATE SET status = EXCLUDED.status;
                """,
                chunk
            )
            print(f"Ingested {offset + len(chunk)}/{num_records} rows...")
    conn.commit()
    
    duration = time.time() - start_time
    throughput = num_records / duration
    print(f"Ingestion Finished: {num_records} records in {duration:.2f}s ({throughput:.2f} rows/sec)")
    return throughput

def concurrent_worker(worker_id, num_ops, data):
    """Worker function representing a concurrent university staff member."""
    conn = get_connection()
    students = data["students"]
    courses = data["courses"]
    semester_id = data["active_semester_id"]
    enrollments = data["enrollments"]
    
    latencies = {
        "enroll": [],
        "attendance": [],
        "result": []
    }
    
    success_count = 0
    failure_count = 0
    
    for _ in range(num_ops):
        op_type = random.choice(["enroll", "attendance", "result"])
        
        if op_type == "enroll":
            student = random.choice(students)
            # Find a course in same department or random
            course = random.choice(courses)
            
            t0 = time.time()
            try:
                # Triggers will check course capacity
                enrollment_ops.enroll_student(conn, student[0], course[0], semester_id)
                latencies["enroll"].append(time.time() - t0)
                success_count += 1
            except Exception:
                # Capacity limits will throw errors, count as valid execution path
                latencies["enroll"].append(time.time() - t0)
                failure_count += 1
                
        elif op_type == "attendance":
            if not enrollments:
                continue
            enrollment = random.choice(enrollments)
            status = random.choice(["Present", "Absent", "Late", "Excused"])
            session_date = datetime.date.today() - datetime.timedelta(days=random.randint(0, 10))
            
            t0 = time.time()
            try:
                attendance_ops.mark_attendance(conn, enrollment[0], session_date, status)
                latencies["attendance"].append(time.time() - t0)
                success_count += 1
            except Exception:
                failure_count += 1
                
        elif op_type == "result":
            if not enrollments:
                continue
            enrollment = random.choice(enrollments)
            marks = round(random.uniform(50.0, 100.0), 2)
            
            t0 = time.time()
            try:
                # Cascades to GPA, CGPA and transcript regeneration
                result_ops.submit_result(conn, enrollment[0], marks, 100.0, True)
                latencies["result"].append(time.time() - t0)
                success_count += 1
            except Exception:
                failure_count += 1
                
    conn.close()
    return latencies, success_count, failure_count

def run_concurrent_simulation(data, num_threads=20, ops_per_thread=50):
    """Runs a concurrent multi-threaded simulation of DB transactions."""
    total_ops = num_threads * ops_per_thread
    print(f"\n--- Running Concurrent User Test ({num_threads} threads, {ops_per_thread} ops/thread) ---")
    
    start_time = time.time()
    
    all_latencies = {
        "enroll": [],
        "attendance": [],
        "result": []
    }
    
    total_success = 0
    total_failure = 0
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [
            executor.submit(concurrent_worker, i, ops_per_thread, data)
            for i in range(num_threads)
        ]
        
        for future in as_completed(futures):
            worker_latencies, success, failure = future.result()
            total_success += success
            total_failure += failure
            for op in all_latencies:
                all_latencies[op].extend(worker_latencies[op])
                
    duration = time.time() - start_time
    overall_throughput = total_ops / duration
    
    print("\n" + "="*70)
    print("CONCURRENT TRANSACTION WORKLOAD REPORT".center(70))
    print("="*70)
    print(f"Total Transactions: {total_ops} | Duration: {duration:.2f}s | Throughput: {overall_throughput:.2f} tx/sec")
    print(f"Success Count: {total_success} | Failures (Incl. capacity limits): {total_failure}")
    print("-"*70)
    print(f"{'Operation':<15} | {'Count':<6} | {'Avg (ms)':<10} | {'p50 (ms)':<10} | {'p95 (ms)':<10} | {'p99 (ms)':<10}")
    print("-"*70)
    
    for op_name, lats in all_latencies.items():
        if not lats:
            print(f"{op_name:<15} | {'0':<6} | {'N/A':<10} | {'N/A':<10} | {'N/A':<10} | {'N/A':<10}")
            continue
            
        # Convert seconds to milliseconds
        lats_ms = [l * 1000 for l in lats]
        avg = sum(lats_ms) / len(lats_ms)
        p50 = statistics.median(lats_ms)
        p95 = statistics.quantiles(lats_ms, n=20)[18]  # 95th percentile
        p99 = statistics.quantiles(lats_ms, n=100)[98] # 99th percentile
        
        print(f"{op_name:<15} | {len(lats):<6} | {avg:>10.2f} | {p50:>10.2f} | {p95:>10.2f} | {p99:>10.2f}")
    print("="*70)

def run_stress_test():
    conn = get_connection()
    try:
        data = get_db_records(conn)
    except Exception as e:
        print(f"Database contains no schema or records yet: {e}")
        print("Please initialize and seed database first.")
        conn.close()
        return
        
    conn.close()
    
    # 1. Run Bulk Ingest Ingestion Load
    run_bulk_insert_test(get_connection(), num_records=100000)
    
    # 2. Run Concurrent User Simulation
    run_concurrent_simulation(data, num_threads=20, ops_per_thread=50)

if __name__ == "__main__":
    run_stress_test()
