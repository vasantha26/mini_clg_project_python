from ..extensions import db


class Timetable(db.Model):
    __tablename__ = 'timetable'

    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)  # 1, 2, 3, 4
    section = db.Column(db.String(1), nullable=False)  # A, B, C
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday to 6=Sunday
    period = db.Column(db.Integer, nullable=False)  # 1-8
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    room = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    staff = db.relationship('Staff', backref='timetable_entries')

    __table_args__ = (
        db.UniqueConstraint('department_id', 'year', 'section', 'day_of_week', 'period',
                            name='unique_timetable_slot'),
    )

    @staticmethod
    def get_day_name(day_num):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return days[day_num] if 0 <= day_num <= 6 else ''


class PeriodTiming(db.Model):
    __tablename__ = 'period_timings'

    id = db.Column(db.Integer, primary_key=True)
    period = db.Column(db.Integer, unique=True, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_break = db.Column(db.Boolean, default=False)
    break_name = db.Column(db.String(50))  # Lunch, Tea Break, etc.
