from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # student, staff, management, hod
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    student = db.relationship('Student', backref='user', uselist=False, cascade='all, delete-orphan')
    staff = db.relationship('Staff', backref='user', uselist=False, cascade='all, delete-orphan')
    management = db.relationship('Management', backref='user', uselist=False, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_student(self):
        return self.role == 'student'

    def is_staff(self):
        return self.role in ['staff', 'hod']

    def is_management(self):
        return self.role == 'management'

    def is_hod(self):
        return self.role == 'hod'

    def get_display_name(self):
        if self.student:
            return self.student.name
        elif self.staff:
            return self.staff.name
        elif self.management:
            return self.management.name
        return self.username


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    roll_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)  # 1, 2, 3, 4
    semester = db.Column(db.Integer, nullable=False)  # 1-8
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    section = db.Column(db.String(1), nullable=False)  # A, B, C
    phone = db.Column(db.String(15))
    address = db.Column(db.Text)
    admission_date = db.Column(db.Date)

    # Relationships
    attendance_records = db.relationship('AttendanceRecord', backref='student', lazy='dynamic')
    marks = db.relationship('Marks', backref='student', lazy='dynamic')
    fees = db.relationship('StudentFees', backref='student', lazy='dynamic')
    book_issues = db.relationship('BookIssue', backref='student', lazy='dynamic')
    complaints = db.relationship('Complaint', backref='student', lazy='dynamic')
    feedbacks = db.relationship('Feedback', backref='student', lazy='dynamic')


class Staff(db.Model):
    __tablename__ = 'staff'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    designation = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(15))
    qualification = db.Column(db.String(100))
    joining_date = db.Column(db.Date)

    # Relationships
    attendance_sessions = db.relationship('AttendanceSession', backref='staff', lazy='dynamic')
    subjects = db.relationship('Subject', secondary='staff_subjects', backref='staff_members')
    feedbacks_received = db.relationship('Feedback', backref='target_staff', lazy='dynamic',
                                         foreign_keys='Feedback.target_staff_id')


# Association table for staff-subject mapping
staff_subjects = db.Table('staff_subjects',
    db.Column('staff_id', db.Integer, db.ForeignKey('staff.id'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id'), primary_key=True)
)


class Management(db.Model):
    __tablename__ = 'management'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(15))

    # Relationships
    notices_posted = db.relationship('Notice', backref='posted_by_user', lazy='dynamic')
