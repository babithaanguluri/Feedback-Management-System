# Feedback Management System (FMS)

A complete, production-ready Django web application for college feedback management built with Bootstrap 5, featuring role-based access control, real-time dashboard analytics, search & multi-level filters, dynamic credentials generation, and interactive star ratings.

---

## Key Features

- **Role-Based Separation**:
  - **Admin**: Full control over student records, teacher records, submitted feedback, and analytics.
  - **Student**: Direct access to submit feedback and change password.
- **No Public Registration**: Students are created solely by administrators.
- **Automatic Credentials**:
  - `Username = Student Name`
  - `Password = Student Roll Number`
- **Dynamic Admin Dashboard**: Real database counts for Total Students, Total Teachers, and Total Feedback.
- **Recent Feedback Table**: Includes star ratings, timestamps, and delete actions with confirmation modals.
- **Search & Filtering**: Real-time search across student names, roll numbers, and teachers, with department and teacher dropdown filters that work synchronously.
- **Interactive 5-Star Rating**: Dynamic hover and selection effects with live rating feedback.
- **Prefilled & Read-Only**: Student details (Roll No, Name, Department) are automatically populated and locked during submission.
- **Duplicate Prevention**: Post-Redirect-Get implementation prevents duplicate submissions on refresh.

---

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/babithaanguluri/Feedback-Management-System.git
cd Feedback-Management-System
```

### 2. Install Dependencies
```bash
pip install django
```

### 3. Apply Migrations
```bash
python manage.py migrate
```

### 4. Seed Initial Data
```bash
python manage.py seed_data
```

### 5. Run the Server
```bash
python manage.py runserver 127.0.0.1:8000
```

---

## Default Credentials

| Portal | URL | Username | Password |
|---|---|---|---|
| **Admin Portal** | `http://127.0.0.1:8000/admin-login/` | `admin` | `admin123` |
| **Student** | `http://127.0.0.1:8000/student-login/` | `Rahul` | `23CS101` |
| **Student** | `http://127.0.0.1:8000/student-login/` | `Priya` | `23CS102` |
| **Student** | `http://127.0.0.1:8000/student-login/` | `Arjun Kumar` | `23CS103` |

---

## 🛠️ Technology Stack

- **Backend**: Python 3.14, Django 6.1
- **Database**: SQLite
- **Frontend**: HTML5, Vanilla CSS, Bootstrap 5, Bootstrap Icons, Google Font Inter
