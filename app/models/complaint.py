from datetime import datetime
from ..extensions import db


class Complaint(db.Model):
    __tablename__ = 'complaints'

    id = db.Column(db.Integer, primary_key=True)
    complaint_type = db.Column(db.String(20), nullable=False)  # utility, academic
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, resolved, closed
    priority = db.Column(db.String(10), default='normal')  # low, normal, high
    submitted_by = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)

    # Relationships
    responses = db.relationship('ComplaintResponse', backref='complaint', lazy='dynamic',
                                cascade='all, delete-orphan')
    assigned_staff = db.relationship('Staff', backref='assigned_complaints')


class ComplaintResponse(db.Model):
    __tablename__ = 'complaint_responses'

    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=False)
    responder_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    responder = db.relationship('User', backref='complaint_responses')
