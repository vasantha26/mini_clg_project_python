# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Flask-based college management system with role-based access control. Supports four user types: student, staff, hod (Head of Department), and management.

## Commands

```bash
# Install dependencies
pip install -r college_management/requirements.txt

# Seed database with test data (drops existing data)
python college_management/seed.py

# Run development server (port 5000)
python college_management/run.py
```

**Test Credentials** (after seeding):
- Management: admin / admin123
- HOD: hod1 / hod123
- Staff: staff1, staff2, staff3 / staff123
- Students: student1-10 / student123

## Architecture

### App Factory Pattern
Entry point is `college_management/run.py` which calls `create_app()` from `college_management/app/__init__.py`. The factory initializes Flask extensions and registers blueprints.

### Extensions (`app/extensions.py`)
- `db` - Flask-SQLAlchemy
- `login_manager` - Flask-Login
- `csrf` - Flask-WTF CSRF protection

### Blueprints (`app/blueprints/`)
Each module follows the same pattern:
- `__init__.py` - Creates Blueprint, imports routes
- `routes.py` - Route handlers
- `forms.py` - WTForms (where needed)

| Blueprint | URL Prefix | Purpose |
|-----------|------------|---------|
| auth | / | Login/logout |
| dashboard | / | Role-specific dashboards |
| attendance | /attendance | Mark and view attendance |
| marks | /marks | Exams and results |
| fees | /fees | Fee management |
| library | /library | Book management |
| complaints | /complaints | Student complaints |
| feedback | /feedback | Staff feedback |
| notices | /notices | Announcements |
| timetable | /timetable | Class schedules |
| notifications | /notifications | User notifications |
| usermanagement | /manage | User CRUD operations |

### Models (`app/models/`)
Core entities:
- `User` - Base user with role field, has one-to-one with Student/Staff/Management
- `Student` - Links to Department, has attendance/marks/fees/complaints/feedback
- `Staff` - Links to Department, has subjects (many-to-many via `staff_subjects`)
- `Department` - Has HOD (Staff), students, subjects
- `Subject` - Has attendance sessions, exams, timetable entries

### Role-Based Access (`app/utils/decorators.py`)
Route decorators: `@role_required('staff', 'management')`, `@student_required`, `@staff_required`, `@management_required`, `@hod_required`

### Authentication
- Students: Roll number + date of birth
- Staff/HOD/Management: Username + password + role selection

### Configuration (`app/config.py`)
- `SECRET_KEY` - From env or default dev key
- `DATABASE_URL` - From env or SQLite at `instance/college.db`
