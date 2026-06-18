# University Management System - Web Application Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Database

Edit `config.py` and update the database credentials:

```python
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "your_password",  # ← Update this
    "dbname": "university_db"
}
```

### 3. Initialize Database (First Time Only)

```bash
python main.py
```

Select option **1** to initialize the database.

### 4. Run the Web Application

```bash
python app.py
```

The application will start at: **http://localhost:5000**

---

## Features

### Dashboard
- Overview of system statistics
- Quick access to all major functions
- System status indicator

### Students Management
- ✅ Add new students
- ✅ View student profiles
- ✅ Edit student information
- ✅ View student enrollment, results, and attendance
- ✅ Track CGPA and academic standing
- ✅ Pagination support

### Teachers Management
- ✅ Add new teachers
- ✅ View teacher profiles
- ✅ View assigned courses
- ✅ Manage course assignments

### Courses Management
- ✅ Add new courses
- ✅ View all courses with details
- ✅ Assign instructors
- ✅ View enrolled students per course
- ✅ Track course credits and department

### Enrollment Management
- ✅ Enroll students in courses
- ✅ View all enrollments
- ✅ Drop courses
- ✅ Track enrollment history

### Attendance Management
- ✅ Mark student attendance
- ✅ View attendance records
- ✅ Calculate attendance percentage
- ✅ Filter by date and course

### Results Management
- ✅ Submit student grades
- ✅ View results by student
- ✅ Track marks and letter grades
- ✅ Automatic GPA calculation

---

## Project Structure

```
University managment system/
├── app.py                     # Flask web application
├── config.py                  # Database configuration
├── requirements.txt           # Python dependencies
├── walkThrough.md            # Complete user guide
├── templates/                 # HTML templates
│   ├── base.html             # Base template
│   ├── index.html            # Dashboard
│   ├── students_list.html    # All students
│   ├── add_student.html      # Add student form
│   ├── student_profile.html  # Student details
│   ├── edit_student.html     # Edit student
│   ├── teachers_list.html    # All teachers
│   ├── add_teacher.html      # Add teacher form
│   ├── teacher_profile.html  # Teacher details
│   ├── courses_list.html     # All courses
│   ├── add_course.html       # Add course form
│   ├── course_profile.html   # Course details
│   ├── enrollments_list.html # All enrollments
│   ├── add_enrollment.html   # Enroll student form
│   ├── attendance.html       # Mark attendance
│   ├── attendance_records.html # View attendance
│   ├── results.html          # Submit grades
│   ├── student_results.html  # View results
│   ├── 404.html              # Not found error
│   └── 500.html              # Server error
└── static/                    # Static files
    └── style.css             # Custom CSS
```

---

## Database Schema

### Tables
1. **department** - Department information
2. **student** - Student records
3. **teacher** - Teacher information
4. **course** - Course details
5. **enrollment** - Student enrollments
6. **attendance** - Attendance records
7. **result** - Student grades
8. **academic_standing** - Standing definitions
9. **grade_scale** - Grade to GPA mapping
10. **transcript** - Academic transcripts

### Relationships
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

## API Endpoints

### Students
- `GET /api/students/<id>/courses` - Get student's courses
- `GET /api/students/<id>/courses` - Get enrolled courses

### Courses
- `GET /api/courses` - Get all courses

---

## Browser Compatibility

- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Opera 76+

---

## Troubleshooting

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/macOS
lsof -i :5000
kill -9 <PID>
```

### Database Connection Error
- Ensure PostgreSQL is running
- Verify credentials in `config.py`
- Check PostgreSQL port (default: 5432)

### Module Not Found
```bash
pip install --upgrade -r requirements.txt
```

### 500 Internal Server Error
- Check the terminal for error messages
- Verify database connection
- Check browser console for client errors

---

## Notes

- The system uses Bootstrap 5 for responsive UI
- All timestamps are in UTC
- GPA and CGPA are calculated automatically by database triggers
- The system supports pagination for large datasets
- All forms include validation on both client and server sides

---

## Security Notes

- Change the Flask secret key in production
- Use environment variables for database credentials
- Enable HTTPS in production
- Implement user authentication and authorization
- Validate all user inputs

---

## Performance Tips

1. **Database Indexing**: Already configured for optimal queries
2. **Caching**: Consider adding Redis for frequently accessed data
3. **Pagination**: Default 20 items per page for large tables
4. **Database Connection Pooling**: Already implemented

---

## Support & Documentation

- Full user guide: See [walkThrough.md](walkThrough.md)
- Database schema: See [sql/schema.sql](sql/schema.sql)
- API documentation in [app.py](app.py)

---

**Last Updated**: December 2024
