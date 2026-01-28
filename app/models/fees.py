from datetime import datetime
from ..extensions import db


class FeeStructure(db.Model):
    __tablename__ = 'fee_structure'

    id = db.Column(db.Integer, primary_key=True)
    academic_year = db.Column(db.String(10), nullable=False)  # 2024-25
    year = db.Column(db.Integer, nullable=False)  # Student year 1, 2, 3, 4
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    fee_type = db.Column(db.String(50), nullable=True)  # Optional fee type
    amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    student_fees = db.relationship('StudentFees', backref='fee_structure', lazy='dynamic')


class StudentFees(db.Model):
    __tablename__ = 'student_fees'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    fee_structure_id = db.Column(db.Integer, db.ForeignKey('fee_structure.id'), nullable=False)
    amount_due = db.Column(db.Float, nullable=False)
    amount_paid = db.Column(db.Float, default=0.0)
    payment_status = db.Column(db.String(20), default='pending')  # pending, partial, paid
    payment_date = db.Column(db.DateTime)
    transaction_id = db.Column(db.String(50))
    remarks = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('student_id', 'fee_structure_id', name='unique_student_fee'),
    )

    def update_status(self):
        if self.amount_paid >= self.amount_due:
            self.payment_status = 'paid'
        elif self.amount_paid > 0:
            self.payment_status = 'partial'
        else:
            self.payment_status = 'pending'

    @property
    def balance(self):
        return self.amount_due - self.amount_paid
