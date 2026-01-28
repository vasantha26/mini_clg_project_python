# College Management System

A comprehensive Flask-based college management system with role-based access control supporting students, staff, HOD (Head of Department), and management users.

## Features

- **Authentication** - Role-based login system
- **Attendance Management** - Mark and view student attendance
- **Marks & Exams** - Manage exams and results
- **Fee Management** - Track and manage student fees
- **Library System** - Book management and tracking
- **Complaints** - Student complaint submission and tracking
- **Feedback** - Staff feedback system
- **Notices** - Announcements and notifications
- **Timetable** - Class schedule management
- **User Management** - CRUD operations for all user types

## Tech Stack

- **Backend**: Python, Flask
- **Database**: SQLite (SQLAlchemy ORM)
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF, WTForms
- **Frontend**: HTML, CSS, JavaScript

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/vasantha26/mini_clg_project_python.git
   cd mini_clg_project_python
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Seed database with test data**
   ```bash
   python seed.py
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

6. **Access the application**

   Open your browser and navigate to: `http://localhost:5000`

## Test Credentials

After seeding the database, use these credentials to login:

| Role | Username | Password |
|------|----------|----------|
| Management | admin | admin123 |
| HOD | hod1 | hod123 |
| Staff | staff1, staff2, staff3 | staff123 |
| Student | student1 - student10 | student123 |

## Project Structure

```
mini_clg_project_python/
├── app/
│   ├── __init__.py          # App factory
│   ├── config.py            # Configuration
│   ├── extensions.py        # Flask extensions
│   ├── blueprints/          # Route modules
│   │   ├── auth/            # Authentication
│   │   ├── dashboard/       # Role-specific dashboards
│   │   ├── attendance/      # Attendance management
│   │   ├── marks/           # Exams and results
│   │   ├── fees/            # Fee management
│   │   ├── library/         # Library system
│   │   ├── complaints/      # Complaint handling
│   │   ├── feedback/        # Feedback system
│   │   ├── notices/         # Announcements
│   │   ├── timetable/       # Class schedules
│   │   ├── notifications/   # User notifications
│   │   └── usermanagement/  # User CRUD
│   ├── models/              # Database models
│   ├── templates/           # HTML templates
│   ├── services/            # Business logic
│   └── utils/               # Utility functions
├── static/                  # CSS, JS, images
├── instance/                # Database file
├── requirements.txt         # Dependencies
├── run.py                   # Entry point
└── seed.py                  # Database seeder
```

## User Roles

### Management
- Full system access
- User management (create, update, delete)
- View all reports and analytics

### HOD (Head of Department)
- Department-level access
- Manage staff and students in department
- View department reports

### Staff
- Mark attendance
- Enter marks and grades
- View assigned subjects

### Student
- View attendance
- View marks and results
- Pay fees
- Submit complaints
- Access library

## License

This project is for educational purposes.

## Author

Vasantha
