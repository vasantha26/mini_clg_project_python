from datetime import datetime
from ..extensions import db


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    notification_type = db.Column(db.String(30), nullable=False)
    # Types: low_attendance, utility_complaint, academic_complaint,
    #        staff_feedback, general_feedback, new_notice, result_uploaded
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    reference_type = db.Column(db.String(30))  # complaint, feedback, notice, marks, attendance
    reference_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def mark_as_read(self):
        self.is_read = True
