# University Management System — Walk Through Guide

## Overview

The University Management System is a comprehensive PostgreSQL-based application designed to manage students, teachers, courses, enrollments, attendance, results, and transcripts. This guide walks you through the features and how to use both the CLI and Web-based interfaces.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation & Setup](#installation--setup)
3. [Database Initialization](#database-initialization)
4. [CLI Usage](#cli-usage)
5. [Web Interface Usage](#web-interface-usage)
6. [Core Features](#core-features)
7. [API Endpoints](#api-endpoints)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- **PostgreSQL 12+** (running locally on `localhost:5432`)
- **Python 3.9+**
- **Internet connection** (for initial setup)

### Verify PostgreSQL Installation

```bash
psql --version
psql -U postgres -h localhost -c "SELECT version();"
```

---

## Installation & Setup

### Step 1: Clone/Setup Project

```bash
cd "d:\Data Science PUCIT\4th Semester\DB\University managment system"
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
pip install flask flask-cors
```

### Step 3: Configure Database Connection

Edit `config.py` and ensure the credentials match your PostgreSQL setup:

```python
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "your_password",  # ← Update this
    "dbname": "university_db"
}
```

---

## Database Initialization

### Create Database & Tables

Run the initialization script:

```bash
python main.py
```

Select option **1** from the CLI menu:

```
==================================================
 UNIVERSITY MANAGEMENT SYSTEM - MAIN MENU
==================================================
1. Initialize Database
2. Seed Sample Data
3. Student Operations
4. Teacher Operations
5. Enrollment Operations
6. Attendance Operations
7. Result Operations
8. Transcript Operations
9. Benchmarks
10. Stress Tests
0. Exit
```

This will:
- ✅ Create `university_db` database
- ✅ Create all 10 tables (department, student, teacher, course, enrollment, etc.)
- ✅ Set up triggers and functions
- ✅ Create indexes for performance

### Seed Sample Data (Optional)

Select option **2** to populate the database with:
- 1,000 students across departments
- 100 courses
- 200 teachers
- 10,000+ enrollments

**Warning**: This takes 2-5 minutes. Ensure you have 2GB+ disk space available.

---

## CLI Usage

### 1. Student Operations

```
Select option 3 from the main menu
```

#### Add New Student

```
1. Add New Student
   Enter:
   - Department ID (e.g., 1, 2, 3)
   - Roll Number (e.g., SP23-001)
   - First Name
   - Last Name
   - Email
   - Date of Birth (YYYY-MM-DD)
   - Admission Date (YYYY-MM-DD)
```

#### View Student Profile

```
3. View Student Profile
   Enter student ID to see:
   - Personal information
   - Department & roll number
   - GPA & CGPA (auto-calculated)
   - Academic standing
   - Enrollment count
```

#### List Students

```
4. List Students
   View all students with pagination (100 per page)
```

### 2. Teacher Operations

```
Select option 4 from the main menu
```

#### Add New Teacher

```
1. Add New Teacher
   Enter:
   - Department ID
   - First Name
   - Last Name
   - Email
   - Hire Date (YYYY-MM-DD)
   - Designation (e.g., Professor, Assistant Professor)
```

#### Assign Course to Teacher

```
2. Assign Course to Teacher
   Enter:
   - Teacher ID
   - Course ID
```

### 3. Enrollment Operations

```
Select option 5 from the main menu
```

#### Enroll Student in Course

```
1. Enroll Student in Course
   Enter:
   - Student ID
   - Course ID
   - Enrollment Date (YYYY-MM-DD)
```

#### Drop Course

```
2. Drop Course
   - Student ID
   - Course ID
```

### 4. Attendance Operations

```
Select option 6 from the main menu
```

#### Mark Attendance

```

1. Mark Attendance
   Enter:
   - Student ID
   - Course ID
   - Attendance Date (YYYY-MM-DD)
   - Status (Present/Absent)
```

#### View Attendance Summary

```
2. View Attendance Summary
   - Shows attendance percentage per course
```

### 5. Result Operations

```
Select option 7 from the main menu
```

#### Submit Grades

```
1. Submit Grades
   Enter:
   - Student ID
   - Course ID
   - Marks (0-100)
   - Grade (A, B, C, D, F)
```

#### View Results

```
2. View Results
   - Shows all grades for a student
```

### 6. Transcript Operations

```
Select option 8 from the main menu
```

#### Generate Transcript

```
1. Generate Transcript
   Enter Student ID to generate official transcript showing:
   - All courses taken
   - Grades & marks
   - CGPA
   - Academic standing
```

---

## Web Interface Usage

### Starting the Web Server

```bash
python app.py
```

Server runs at: **http://localhost:5000**

### UI Features & Dark Mode

The web interface features a modern, responsive design with:

#### Dark Mode Toggle
- **Location**: Top-right corner of the navbar (moon/sun icon)
- **Usage**: Click the moon icon (🌙) to enable dark mode, sun icon (☀️) to return to light mode
- **Preference**: Your choice is automatically saved in your browser
- **Applies to**: All pages (Dashboard, Students, Teachers, Courses, Forms, etc.)

#### Modern Design Features
- **3D Effects**: Cards have elevated shadows and smooth hover animations
- **Smooth Transitions**: All UI elements transition smoothly when colors change
- **Gradient Accents**: Buttons and headers use gradient backgrounds
- **Responsive Layout**: Optimized for desktop, tablet, and mobile devices
- **Clean Aesthetic**: Minimalist design with focus on usability

#### Color Schemes
**Light Mode:**
- Clean white backgrounds
- Dark text for readability
- Blue gradient accents

**Dark Mode:**
- Dark navy/slate backgrounds
- Light text for eye comfort
- Same blue gradient accents with enhanced contrast

### Dashboard

Main page shows:
- ✅ System status
- ✅ Quick statistics (total students, teachers, courses)
- ✅ Navigation menu
- ✅ Dark mode toggle button

### 1. Students Management

**URL**: `http://localhost:5000/students`

#### Add New Student

```
Form fields:
- Department ID
- Roll Number
- First Name
- Last Name
- Email
- Date of Birth (picker)
- Admission Date (picker)

Action: Submit → Student created successfully
```

#### View All Students

```
Displays:
- Student ID
- Roll Number
- Full Name
- Email
- Department
- GPA
- Academic Standing

Features:
- Search by name
- Filter by department
- View detailed profile
- Edit student info
- Delete student
```

#### Student Profile

**URL**: `http://localhost:5000/student/<id>`

```
Shows:
- Personal information
- Department details
- Academic metrics (GPA, CGPA)
- Enrollment history
- Courses
- Attendance summary
- Results/Grades
- Full transcript
```

### 2. Teachers Management

**URL**: `http://localhost:5000/teachers`

#### Add New Teacher

```
Form fields:
- Department ID
- First Name
- Last Name
- Email
- Hire Date (picker)
- Designation

Action: Submit → Teacher created successfully
```

#### View All Teachers

```
Displays:
- Teacher ID
- Full Name
- Email
- Department
- Designation
- Hire Date

Features:
- Search by name
- Filter by department
- View detailed profile
- Assign courses
- Delete teacher
```

#### Teacher Profile

**URL**: `http://localhost:5000/teacher/<id>`

```
Shows:
- Personal information
- Department details
- Assigned courses
- Teaching schedule
- Student feedback (if available)
```

### 3. Courses Management

**URL**: `http://localhost:5000/courses`

#### Add New Course

```
Form fields:
- Department ID
- Course Name
- Course Code
- Credits
- Teacher ID (optional)

Action: Submit → Course created successfully
```

#### View All Courses

```
Displays:
- Course ID
- Course Name & Code
- Department
- Credits
- Assigned Teacher
- Enrollment Count

Features:
- Search by name/code
- Filter by department
- View enrolled students
- Edit course info
```

### 4. Enrollments Management

**URL**: `http://localhost:5000/enrollments`

#### Enroll Student

```
Form fields:
- Student ID
- Course ID
- Enrollment Date

Action: Submit → Enrollment created successfully
```

#### View All Enrollments

```
Displays:
- Student Name
- Course Name
- Enrollment Date
- Status (Active/Dropped)

Features:
- Search by student/course
- Drop course
- View enrollment details
```

### 5. Attendance Management

**URL**: `http://localhost:5000/attendance`

#### Mark Attendance

```
Form:
- Student ID
- Course ID
- Date
- Status (Present/Absent)

Action: Submit → Attendance recorded
```

#### Attendance Report

```
Displays:
- Student attendance by course
- Attendance percentage
- Present/Absent count

Features:
- Filter by date range
- Download report (CSV)
```

### 6. Results Management

**URL**: `http://localhost:5000/results`

#### Submit Grade

```
Form:
- Student ID
- Course ID
- Marks (0-100)
- Grade (A, B, C, D, F)

Action: Submit → Grade recorded
```

#### View Results

```
Displays:
- Student results by course
- Marks & Grade
- GPA calculation

Features:
- Filter by student/course
- Download report (CSV)
- Print transcript
```

### 7. Reports & Analytics

**URL**: `http://localhost:5000/reports`

#### Dashboard Analytics

```
Shows:
- Total students/teachers/courses
- Average GPA
- Enrollment trends
- Recent activities
```

#### Generate Reports

```
Available reports:
1. Student Academic Performance
2. Attendance Summary
3. Results Summary
4. Department Analytics
5. Course Utilization

Export: PDF, CSV, Excel
```

---

## Core Features

### Automated Calculations (via Triggers)

- **GPA Calculation**: Automatically updated when grades are submitted
- **CGPA Calculation**: Cumulative GPA across all courses
- **Attendance Percentage**: Auto-calculated from attendance records
- **Academic Standing**: Determined by GPA (Excellent, Good, Satisfactory, Poor)

### Data Integrity

- **Foreign Key Constraints**: Prevent orphaned records
- **Unique Constraints**: Email, roll number, course code
- **Check Constraints**: Valid grades (0-100), valid attendance status
- **NOT NULL Constraints**: Required fields enforced

### Performance Features

- **Composite Indexes**: On frequently queried columns
- **Partial Indexes**: On active enrollments
- **Query Optimization**: EXPLAIN ANALYZE available in CLI

---

## API Endpoints

If using FastAPI instead of Flask, here are the REST endpoints:

### Students

```
GET    /api/students                    → List all students
POST   /api/students                    → Create new student
GET    /api/students/<id>               → Get student details
PUT    /api/students/<id>               → Update student
DELETE /api/students/<id>               → Delete student
GET    /api/students/<id>/transcript    → Get transcript
GET    /api/students/<id>/attendance    → Get attendance records
GET    /api/students/<id>/results       → Get results
```

### Teachers

```
GET    /api/teachers                    → List all teachers
POST   /api/teachers                    → Create new teacher
GET    /api/teachers/<id>               → Get teacher details
PUT    /api/teachers/<id>               → Update teacher
DELETE /api/teachers/<id>               → Delete teacher
GET    /api/teachers/<id>/schedule      → Get teaching schedule
GET    /api/teachers/<id>/courses       → Get assigned courses
```

### Courses

```
GET    /api/courses                     → List all courses
POST   /api/courses                     → Create new course
GET    /api/courses/<id>                → Get course details
PUT    /api/courses/<id>                → Update course
DELETE /api/courses/<id>                → Delete course
GET    /api/courses/<id>/students       → Get enrolled students
```

### Enrollments

```
GET    /api/enrollments                 → List all enrollments
POST   /api/enrollments                 → Enroll student
DELETE /api/enrollments/<id>            → Drop course
GET    /api/enrollments/<id>            → Get enrollment details
```

### Attendance

```
POST   /api/attendance                  → Mark attendance
GET    /api/attendance/<student_id>     → Get student attendance
GET    /api/attendance/<student_id>/<course_id> → Get course attendance
```

### Results

```
POST   /api/results                     → Submit grade
GET    /api/results/<student_id>        → Get student results
GET    /api/results/<student_id>/<course_id> → Get course result
PUT    /api/results/<id>                → Update grade
```

---

## Database Schema Overview

### Tables

1. **department** - Departments (CS, EE, BBA, etc.)
2. **student** - Student records with GPA, CGPA, academic standing
3. **teacher** - Teacher information and details
4. **course** - Course details, credits, assigned teacher
5. **enrollment** - Student course registrations
6. **attendance** - Daily attendance records
7. **result** - Grades and marks
8. **transcript** - Academic transcript view
9. **academic_standing** - Standing lookup table
10. **grade_scale** - Grade to GPA mapping

### Key Relationships

```
department (1) ──→ (M) student
department (1) ──→ (M) teacher
department (1) ──→ (M) course
course (1) ──→ (M) enrollment
student (1) ──→ (M) enrollment
student (1) ──→ (M) attendance
student (1) ──→ (M) result
teacher (1) ──→ (M) course
```

---

## Troubleshooting

### Connection Issues

**Error**: `psycopg2.OperationalError: could not connect to server`

**Solution**:
```bash
# Check PostgreSQL is running
# Windows: Open Services, find PostgreSQL, restart
# Linux: sudo systemctl restart postgresql
# macOS: brew services restart postgresql

# Verify connection
psql -U postgres -h localhost
```

### Database Not Found

**Error**: `database "university_db" does not exist`

**Solution**:
Run database initialization from the CLI:
```
Option 1: Initialize Database
```

### Permission Denied

**Error**: `permission denied for schema public`

**Solution**:
```bash
psql -U postgres -c "GRANT ALL ON DATABASE university_db TO postgres;"
```

### Web Server Won't Start

**Error**: `Address already in use`

**Solution**:
```bash
# Kill process on port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/macOS:
lsof -i :5000
kill -9 <PID>
```

### Dark Mode Issues

**Issue**: Dark mode not persisting after page reload

**Solution**: Clear browser cache and localStorage:
```javascript
// In browser console:
localStorage.clear();
location.reload();
```

**Issue**: Dark mode toggle button not visible

**Solution**: Ensure you're viewing the latest CSS file:
1. Hard refresh the page: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (macOS)
2. Clear browser cache and cookies
3. If issue persists, check browser developer tools (F12) for CSS errors

**Issue**: Colors look wrong in dark mode

**Solution**: 
1. Verify your browser supports CSS variables (most modern browsers do)
2. Try a different browser to rule out compatibility issues
3. Check that the latest `style_new.css` file is being loaded (not the old `style.css`)
kill -9 <PID>
```

### Slow Queries

**Solution**:
Use the benchmark tool from CLI:
```
Option 9: Benchmarks → Run EXPLAIN ANALYZE
```

---

## Quick Start Checklist

- [ ] PostgreSQL installed and running
- [ ] Python 3.9+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Database credentials configured in `config.py`
- [ ] Database initialized (CLI option 1)
- [ ] Sample data seeded (optional, CLI option 2)
- [ ] Web server started (`python app.py`)
- [ ] Opened `http://localhost:5000` in browser

---

## Support

For issues or questions:
1. Check the **Troubleshooting** section above
2. Review PostgreSQL logs
3. Check Python error messages in terminal
4. Verify database connectivity using `psql`

---

## Version Information

- **System Version**: 1.0
- **Python**: 3.9+
- **PostgreSQL**: 12+
- **Flask**: 2.0+
- **psycopg2**: 2.9+

---

**Last Updated**: December 2024
