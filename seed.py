"""
Seed script to populate initial data for testing.
Run: python seed.py
"""
from datetime import date, time
from app import create_app
from app.extensions import db
from app.models import (
    User, Student, Staff, Management, Department, Subject,
    PeriodTiming, FeeStructure, Book
)

app = create_app()

with app.app_context():
    # Drop and recreate all tables
    db.drop_all()
    db.create_all()

    print("Creating departments...")
    departments = [
        Department(code='CSE', name='Computer Science and Engineering'),
        Department(code='ECE', name='Electronics and Communication Engineering'),
        Department(code='ME', name='Mechanical Engineering'),
        Department(code='CE', name='Civil Engineering'),
    ]
    db.session.add_all(departments)
    db.session.commit()

    print("Creating management users...")
    # Create management user
    mgmt_user = User(username='admin', email='admin@college.edu', role='management')
    mgmt_user.set_password('admin123')
    db.session.add(mgmt_user)
    db.session.flush()

    management = Management(
        user_id=mgmt_user.id,
        employee_id='MGT001',
        name='Admin User',
        designation='Administrator'
    )
    db.session.add(management)

    print("Creating staff users...")
    # Create staff users
    staff_data = [
        ('staff1', 'staff1@college.edu', 'STF001', 'Dr. John Smith', 'Professor', 1),
        ('staff2', 'staff2@college.edu', 'STF002', 'Dr. Jane Doe', 'Associate Professor', 1),
        ('staff3', 'staff3@college.edu', 'STF003', 'Prof. Robert Brown', 'Assistant Professor', 2),
    ]

    for username, email, emp_id, name, designation, dept_id in staff_data:
        user = User(username=username, email=email, role='staff')
        user.set_password('staff123')
        db.session.add(user)
        db.session.flush()

        staff = Staff(
            user_id=user.id,
            employee_id=emp_id,
            name=name,
            department_id=dept_id,
            designation=designation
        )
        db.session.add(staff)

    # Create HOD
    hod_user = User(username='hod1', email='hod@college.edu', role='hod')
    hod_user.set_password('hod123')
    db.session.add(hod_user)
    db.session.flush()

    hod = Staff(
        user_id=hod_user.id,
        employee_id='HOD001',
        name='Dr. Michael Johnson',
        department_id=1,
        designation='Head of Department'
    )
    db.session.add(hod)
    db.session.commit()

    # Update department HOD
    departments[0].hod_id = hod.id
    db.session.commit()

    print("Creating subjects...")
    subjects = [
        Subject(code='CS101', name='Programming Fundamentals', department_id=1, year=1, semester=1),
        Subject(code='CS102', name='Data Structures', department_id=1, year=1, semester=2),
        Subject(code='CS201', name='Database Systems', department_id=1, year=2, semester=3),
        Subject(code='CS202', name='Operating Systems', department_id=1, year=2, semester=4),
        Subject(code='CS301', name='Computer Networks', department_id=1, year=3, semester=5),
        Subject(code='EC101', name='Basic Electronics', department_id=2, year=1, semester=1),
    ]
    db.session.add_all(subjects)
    db.session.commit()

    # Assign subjects to staff
    staff_members = Staff.query.all()
    for i, staff in enumerate(staff_members[:2]):
        staff.subjects.extend(subjects[i*2:(i+1)*2])
    db.session.commit()

    print("Creating student users...")
    # Create students
    for i in range(1, 11):
        user = User(
            username=f'student{i}',
            email=f'student{i}@college.edu',
            role='student'
        )
        user.set_password('student123')
        db.session.add(user)
        db.session.flush()

        student = Student(
            user_id=user.id,
            roll_number=f'21CS{str(i).zfill(3)}',
            name=f'Student {i}',
            year=(i-1)//3 + 1,
            semester=((i-1)//3)*2 + 1,
            department_id=1,
            section='A' if i <= 5 else 'B',
            admission_date=date(2021, 8, 1)
        )
        db.session.add(student)

    db.session.commit()

    print("Creating period timings...")
    timings = [
        PeriodTiming(period=1, start_time=time(9, 0), end_time=time(9, 50)),
        PeriodTiming(period=2, start_time=time(9, 50), end_time=time(10, 40)),
        PeriodTiming(period=3, start_time=time(10, 50), end_time=time(11, 40)),
        PeriodTiming(period=4, start_time=time(11, 40), end_time=time(12, 30)),
        PeriodTiming(period=5, start_time=time(13, 30), end_time=time(14, 20)),
        PeriodTiming(period=6, start_time=time(14, 20), end_time=time(15, 10)),
        PeriodTiming(period=7, start_time=time(15, 20), end_time=time(16, 10)),
        PeriodTiming(period=8, start_time=time(16, 10), end_time=time(17, 0)),
    ]
    db.session.add_all(timings)

    print("Creating fee structures...")
    fee_structures = [
        FeeStructure(
            academic_year='2024-25',
            year=1,
            fee_type='tuition',
            amount=50000,
            due_date=date(2024, 8, 15),
            description='Annual Tuition Fee'
        ),
        FeeStructure(
            academic_year='2024-25',
            year=1,
            fee_type='exam',
            amount=2000,
            due_date=date(2024, 12, 1),
            description='Examination Fee'
        ),
    ]
    db.session.add_all(fee_structures)

    print("Creating library books...")
    books = [
        Book(isbn='978-0-13-468599-1', title='Clean Code', author='Robert C. Martin',
             publisher='Prentice Hall', category='Programming', total_copies=5, available_copies=5),
        Book(isbn='978-0-596-51774-8', title='JavaScript: The Good Parts', author='Douglas Crockford',
             publisher='O\'Reilly', category='Programming', total_copies=3, available_copies=3),
        Book(isbn='978-0-201-63361-0', title='Design Patterns', author='Gang of Four',
             publisher='Addison-Wesley', category='Software Engineering', total_copies=4, available_copies=4),
    ]
    db.session.add_all(books)

    db.session.commit()

    print("\n" + "="*50)
    print("Database seeded successfully!")
    print("="*50)
    print("\nTest Accounts:")
    print("-"*50)
    print("Management:  admin / admin123")
    print("HOD:         hod1 / hod123")
    print("Staff:       staff1 / staff123")
    print("             staff2 / staff123")
    print("             staff3 / staff123")
    print("Students:    student1-10 / student123")
    print("-"*50)
    print("\nRun the app with: python run.py")
