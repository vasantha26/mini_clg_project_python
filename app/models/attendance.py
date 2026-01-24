from datetime import datetime
from ..extensions import db


class AttendanceSession(db.Model):
    __tablename__ = 'attendance_sessions'

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    period = db.Column(db.Integer, nullable=False)  # 1-8
    year = db.Column(db.Integer, nullable=False)
    section = db.Column(db.String(1), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    records = db.relationship('AttendanceRecord', backref='session', lazy='dynamic',
                              cascade='all, delete-orphan')

    __table_args__ = (
        db.UniqueConstraint('subject_id', 'date', 'period', 'section', 'department_id',
                            name='unique_session'),
    )


class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('attendance_sessions.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    is_present = db.Column(db.Boolean, default=False)

    __table_args__ = (
        db.UniqueConstraint('session_id', 'student_id', name='unique_attendance_record'),
    )


class AttendanceSummary(db.Model):
    __tablename__ = 'attendance_summary'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    total_classes = db.Column(db.Integer, default=0)
    attended = db.Column(db.Integer, default=0)
    percentage = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('student_id', 'subject_id', name='unique_summary'),
    )

    def update_percentage(self):
        if self.total_classes > 0:
            self.percentage = (self.attended / self.total_classes) * 100
        else:
            self.percentage = 0.0
