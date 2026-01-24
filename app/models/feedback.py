from datetime import datetime
from ..extensions import db


class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    feedback_type = db.Column(db.String(20), nullable=False)  # general, staff
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer)  # 1-5 stars
    is_anonymous = db.Column(db.Boolean, default=False)
    submitted_by = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    target_staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=True)
    status = db.Column(db.String(20), default='submitted')  # submitted, reviewed, addressed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    subject = db.relationship('Subject', backref='feedbacks')
