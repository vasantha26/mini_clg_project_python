from datetime import datetime, timedelta
from ..extensions import db


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    publisher = db.Column(db.String(100))
    publication_year = db.Column(db.Integer)
    category = db.Column(db.String(50))
    total_copies = db.Column(db.Integer, default=1)
    available_copies = db.Column(db.Integer, default=1)
    location = db.Column(db.String(50))  # Shelf/Rack location
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    issues = db.relationship('BookIssue', backref='book', lazy='dynamic')

    def is_available(self):
        return self.available_copies > 0


class BookIssue(db.Model):
    __tablename__ = 'book_issues'

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='issued')  # issued, returned, overdue
    fine_amount = db.Column(db.Float, default=0.0)
    remarks = db.Column(db.String(200))

    def __init__(self, **kwargs):
        super(BookIssue, self).__init__(**kwargs)
        if not self.due_date:
            self.due_date = datetime.utcnow() + timedelta(days=14)

    def is_overdue(self):
        if self.status == 'returned':
            return False
        return datetime.utcnow() > self.due_date

    def calculate_fine(self, fine_per_day=5.0):
        if self.is_overdue() and self.status != 'returned':
            days_overdue = (datetime.utcnow() - self.due_date).days
            self.fine_amount = days_overdue * fine_per_day
        return self.fine_amount
