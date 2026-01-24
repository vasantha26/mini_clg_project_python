from datetime import datetime
from ..extensions import db


class Exam(db.Model):
    __tablename__ = 'exams'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    exam_type = db.Column(db.String(20), nullable=False)  # assignment, internal, final
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    max_marks = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date)
    year = db.Column(db.Integer, nullable=False)
    section = db.Column(db.String(1), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    marks = db.relationship('Marks', backref='exam', lazy='dynamic', cascade='all, delete-orphan')
    creator = db.relationship('Staff', backref='created_exams')


class Marks(db.Model):
    __tablename__ = 'marks'

    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    marks_obtained = db.Column(db.Float, nullable=True)
    grade = db.Column(db.String(2))
    remarks = db.Column(db.String(200))
    entered_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('exam_id', 'student_id', name='unique_marks'),
    )

    def calculate_grade(self, max_marks):
        if self.marks_obtained is None:
            self.grade = 'AB'  # Absent
            return

        percentage = (self.marks_obtained / max_marks) * 100
        if percentage >= 90:
            self.grade = 'O'
        elif percentage >= 80:
            self.grade = 'A+'
        elif percentage >= 70:
            self.grade = 'A'
        elif percentage >= 60:
            self.grade = 'B+'
        elif percentage >= 50:
            self.grade = 'B'
        elif percentage >= 40:
            self.grade = 'C'
        else:
            self.grade = 'F'
