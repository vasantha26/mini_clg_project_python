from ..extensions import db


class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    hod_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=True)

    # Relationships
    students = db.relationship('Student', backref='department', lazy='dynamic')
    staff_members = db.relationship('Staff', backref='department', lazy='dynamic',
                                    foreign_keys='Staff.department_id')
    subjects = db.relationship('Subject', backref='department', lazy='dynamic')
    timetables = db.relationship('Timetable', backref='department', lazy='dynamic')

    def __repr__(self):
        return f'<Department {self.code}>'


class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)  # 1, 2, 3, 4
    semester = db.Column(db.Integer, nullable=False)  # 1-8
    credits = db.Column(db.Integer, default=3)
    is_lab = db.Column(db.Boolean, default=False)

    # Relationships
    attendance_sessions = db.relationship('AttendanceSession', backref='subject', lazy='dynamic')
    exams = db.relationship('Exam', backref='subject', lazy='dynamic')
    timetable_entries = db.relationship('Timetable', backref='subject', lazy='dynamic')

    def __repr__(self):
        return f'<Subject {self.code}: {self.name}>'
