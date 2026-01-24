from datetime import datetime
from ..extensions import db


class Notice(db.Model):
    __tablename__ = 'notices'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # academic, event, exam, general
    priority = db.Column(db.String(10), default='normal')  # low, normal, high, urgent
    target_audience = db.Column(db.String(50), default='all')  # all, students, staff, year_1, dept_cse, etc.
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    posted_by = db.Column(db.Integer, db.ForeignKey('management.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    publish_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime)
    attachment_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    department = db.relationship('Department', backref='notices')

    def is_expired(self):
        if self.expiry_date:
            return datetime.utcnow() > self.expiry_date
        return False
