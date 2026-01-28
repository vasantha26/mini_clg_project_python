# College Management System
## Software Requirements Specification (SRS)

---

## 1. Introduction

### 1.1 Purpose
This document specifies the requirements for a College Management System designed to automate and streamline academic and administrative processes in educational institutions.

### 1.2 Scope
The system manages students, staff, departments, attendance, examinations, fees, library, complaints, feedback, notices, timetables, and notifications.

### 1.3 Technology Stack
- **Backend**: Python Flask 3.0
- **Database**: SQLite / SQLAlchemy ORM
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF, WTForms
- **Frontend**: HTML Templates (Jinja2), CSS, JavaScript

---

## 2. User Roles and Authentication

### 2.1 User Types
| Role | Description |
|------|-------------|
| Student | Can view attendance, marks, fees, timetable; submit complaints and feedback |
| Staff | Can mark attendance, enter marks, manage library; view assigned classes |
| HOD (Head of Department) | Staff privileges + department-level management |
| Management | Full administrative access to all modules |

### 2.2 Authentication Methods
- **Students**: Login using Roll Number + Date of Birth
- **Staff/HOD/Management**: Login using Username + Password + Role Selection

---

## 3. Functional Requirements

### 3.1 User Management Module
- Create, update, delete user accounts
- Assign roles to users
- Activate/deactivate accounts
- Link users to Student/Staff/Management profiles

### 3.2 Department Management
- Create and manage departments (CSE, ECE, ME, CE, etc.)
- Assign HOD to departments
- Link students and staff to departments

### 3.3 Subject Management
- Create subjects with code, name, credits
- Assign subjects to departments, years, and semesters
- Mark subjects as lab/theory
- Assign staff to subjects (many-to-many relationship)

### 3.4 Attendance Module
**Staff Functions:**
- Create attendance sessions for subjects
- Mark attendance for students (Present/Absent)
- View attendance records

**Student Functions:**
- View personal attendance records
- View attendance summary/percentage

### 3.5 Marks/Examination Module
**Staff Functions:**
- Create exams (Internal, Mid-term, Final, etc.)
- Enter marks for students
- Generate mark reports

**Student Functions:**
- View personal exam results
- View semester-wise results

### 3.6 Fees Module
**Management Functions:**
- Define fee structures (tuition, exam fees)
- Set due dates and academic year
- Upload fee payment records
- Generate pending fee reports

**Student Functions:**
- View fee details and payment status
- View payment history

### 3.7 Library Module
**Staff/Management Functions:**
- Add, update, delete books
- Manage book inventory (total copies, available copies)
- Issue books to students
- Track book returns

**Student Functions:**
- Search books by title, author, ISBN
- View book availability
- View personal borrowed books

### 3.8 Complaints Module
**Student Functions:**
- Submit complaints with category and description
- Track complaint status
- View complaint responses

**Staff/Management Functions:**
- View assigned complaints
- Respond to complaints
- Update complaint status (Pending, In Progress, Resolved)

### 3.9 Feedback Module
**Student Functions:**
- Submit feedback for staff members
- View submitted feedback history

**Staff Functions:**
- View feedback received

**Management Functions:**
- View all feedback
- Generate feedback reports

### 3.10 Notice Board Module
**Management Functions:**
- Create and publish notices
- Set target audience (All, Students, Staff, Department-specific)
- Manage notice visibility

**All Users:**
- View notices relevant to their role
- View notice details

### 3.11 Timetable Module
**Management/HOD Functions:**
- Create timetables for departments
- Assign subjects, staff, and periods
- Define period timings

**Staff Functions:**
- View personal teaching schedule

**Student Functions:**
- View class timetable

### 3.12 Notifications Module
- System-generated notifications for all users
- Mark notifications as read/unread
- Notification categories based on events

---

## 4. Database Schema

### 4.1 Core Tables
| Table | Description |
|-------|-------------|
| users | Base user accounts with role |
| students | Student profiles linked to users |
| staff | Staff profiles linked to users |
| management | Management profiles linked to users |
| departments | Department information |
| subjects | Subject/course information |
| staff_subjects | Staff-subject assignments (M:N) |

### 4.2 Module Tables
| Table | Description |
|-------|-------------|
| attendance_sessions | Attendance session records |
| attendance_records | Individual attendance entries |
| exams | Examination definitions |
| marks | Student marks per exam |
| fee_structures | Fee definitions |
| student_fees | Student payment records |
| books | Library book inventory |
| book_issues | Book borrowing records |
| complaints | Student complaints |
| complaint_responses | Responses to complaints |
| feedbacks | Staff feedback from students |
| notices | Notice board entries |
| timetables | Class schedule entries |
| period_timings | Period time definitions |
| notifications | User notifications |

---

## 5. Non-Functional Requirements

### 5.1 Security
- Password hashing using Werkzeug security
- CSRF protection on all forms
- Session cookie security (HTTPOnly, SameSite)
- Role-based access control on all routes

### 5.2 Usability
- Responsive web interface
- Role-specific dashboards
- Flash messages for user feedback

### 5.3 Performance
- SQLAlchemy lazy loading for relationships
- Database indexing on frequently queried fields

---

## 6. System Architecture

```
college_management/
├── app/
│   ├── __init__.py          # App factory
│   ├── config.py            # Configuration
│   ├── extensions.py        # Flask extensions
│   ├── models/              # Database models
│   ├── blueprints/          # Route modules
│   │   ├── auth/            # Authentication
│   │   ├── dashboard/       # Dashboards
│   │   ├── attendance/      # Attendance management
│   │   ├── marks/           # Examination/marks
│   │   ├── fees/            # Fee management
│   │   ├── library/         # Library management
│   │   ├── complaints/      # Complaint handling
│   │   ├── feedback/        # Staff feedback
│   │   ├── notices/         # Notice board
│   │   ├── timetable/       # Class schedules
│   │   ├── notifications/   # User notifications
│   │   └── usermanagement/  # User CRUD
│   ├── templates/           # HTML templates
│   ├── services/            # Business logic
│   └── utils/               # Utility functions
├── static/                  # CSS, JS files
├── instance/                # SQLite database
├── run.py                   # Application entry
├── seed.py                  # Test data seeder
└── requirements.txt         # Dependencies
```

---

## 7. API Endpoints Summary

| Module | Prefix | Key Endpoints |
|--------|--------|---------------|
| Auth | / | /login, /logout |
| Dashboard | / | /dashboard |
| Attendance | /attendance | /mark, /my-attendance |
| Marks | /marks | /create-exam, /enter, /my-results, /reports |
| Fees | /fees | /upload, /pending-report, /my-fees |
| Library | /library | /search, /manage, /issue, /my-books |
| Complaints | /complaints | /submit, /my-complaints, /assigned |
| Feedback | /feedback | /submit, /my-feedback, /staff-feedback |
| Notices | /notices | /create, /manage, / |
| Timetable | /timetable | /create, /manage, /my-timetable |
| Notifications | /notifications | / |
| User Management | /manage | /users, /students, /staff |

---

## 8. Dependencies

```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Flask-WTF==1.2.1
WTForms==3.1.1
Werkzeug==3.0.1
email-validator==2.1.0
```

---

**Document Version**: 1.0
**Date**: January 2026
