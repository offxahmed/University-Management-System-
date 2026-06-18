# 🚀 QUICK START GUIDE - University Management System Web App

## 📋 Prerequisites

- PostgreSQL running on `localhost:5432`
- Python 3.9+
- 5 minutes

---

## ⚡ 5-Minute Setup

### 1️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 2️⃣ Update Database Credentials
Edit `config.py`:
```python
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "YOUR_PASSWORD",  # ← Change this
    "dbname": "university_db"
}
```

### 3️⃣ Initialize Database
```bash
python main.py
# Press 1 → Initialize Database
```

### 4️⃣ (Optional) Load Sample Data
```bash
python main.py
# Press 2 → Seed Sample Data
# Takes ~2 minutes
```

### 5️⃣ Start Web Server
```bash
python app.py
```

### 6️⃣ Open Browser
Visit: **http://localhost:5000**

---

## 🎯 What You Can Do

| Feature | Path |
|---------|------|
| 👥 **Add Students** | Dashboard → Add New Student |
| 👨‍🏫 **Add Teachers** | Dashboard → Add New Teacher |
| 📚 **Add Courses** | Dashboard → Add New Course |
| 📝 **Enroll Students** | Dashboard → Enroll Student |
| ✅ **Mark Attendance** | Dashboard → Mark Attendance |
| 📊 **Submit Grades** | Dashboard → Submit Results |

---

## 📊 Dashboard Buttons

```
┌─────────────────────────────────────────┐
│    UNIVERSITY MANAGEMENT SYSTEM         │
├─────────────────────────────────────────┤
│ [Add Student] [Add Teacher]             │
│ [Add Course]  [Enroll Student]          │
│ [Attendance]                            │
├─────────────────────────────────────────┤
│ Students: 0  Teachers: 0                │
│ Courses: 0   Enrollments: 0             │
└─────────────────────────────────────────┘
```

---

## 🔍 Features at a Glance

### ✅ Students
- Add/Edit/View profiles
- Track GPA & CGPA
- View courses & grades
- Check attendance

### ✅ Teachers
- Add/Manage teachers
- Assign courses
- View schedules

### ✅ Courses
- Add/Manage courses
- Assign instructors
- View enrollments

### ✅ Enrollment
- Enroll students
- Drop courses
- Track history

### ✅ Attendance
- Mark present/absent
- View records
- Calculate percentage

### ✅ Results
- Submit grades
- View transcripts
- Track progress

---

## ⚙️ Troubleshooting

### ❌ "Address already in use"
```bash
# Change port in app.py
app.run(debug=True, host='0.0.0.0', port=5001)  # Change 5000 to 5001
```

### ❌ "Connection refused"
Check PostgreSQL is running:
```bash
# Windows: Services → PostgreSQL → Start
# Linux: sudo systemctl start postgresql
# macOS: brew services start postgresql
```

### ❌ "Module not found"
```bash
pip install --upgrade -r requirements.txt
```

### ❌ "Database does not exist"
Run initialization again:
```bash
python main.py  # Press option 1
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| `walkThrough.md` | Complete user guide (100+ pages) |
| `WEB_APP_README.md` | Web app documentation |
| `IMPLEMENTATION_SUMMARY.md` | Feature overview |

---

## 💡 Pro Tips

### Add Sample Data Quickly
```bash
python main.py
# Option 2: Seed Sample Data
# Adds 1000 students, 100 courses, 200 teachers
```

### Test Individual Features
1. Add a student
2. Add a course
3. Enroll student in course
4. Mark attendance
5. Submit grades

### View Student Details
- Click "View" on any student in the list
- See profile, grades, attendance all in one place

---

## 🔐 Security Notes

- Change the Flask secret key before deployment
- Use environment variables for passwords
- Enable HTTPS in production
- Implement user authentication for real use

---

## 📞 Need Help?

1. Check `walkThrough.md` for detailed instructions
2. Check terminal for error messages
3. Verify PostgreSQL is running
4. Verify database credentials in `config.py`

---

## 🎉 You're Ready!

```
✅ Dependencies installed
✅ Database configured
✅ Web server running
✅ Ready to use

Open http://localhost:5000 in your browser!
```

---

**Version**: 1.0  
**Last Updated**: December 2024
