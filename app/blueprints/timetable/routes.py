from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import bp
from ...models import Timetable, PeriodTiming, Subject, Staff, Department
from ...extensions import db
from ...utils.decorators import staff_required, student_required
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class TimetableEntryForm(FlaskForm):
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    year = SelectField('Year', coerce=int, choices=[
        (1, '1st Year'), (2, '2nd Year'), (3, '3rd Year'), (4, '4th Year')
    ], validators=[DataRequired()])
    section = StringField('Section', validators=[DataRequired(), Length(max=10)])
    day_of_week = SelectField('Day', coerce=int, choices=[
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday')
    ], validators=[DataRequired()])
    period = SelectField('Period', coerce=int, choices=[
        (1, 'Period 1'), (2, 'Period 2'), (3, 'Period 3'), (4, 'Period 4'),
        (5, 'Period 5'), (6, 'Period 6'), (7, 'Period 7'), (8, 'Period 8')
    ], validators=[DataRequired()])
    subject_id = SelectField('Subject', coerce=int, validators=[DataRequired()])
    staff_id = SelectField('Staff', coerce=int, validators=[DataRequired()])
    room = StringField('Room')
    submit = SubmitField('Add Entry')


@bp.route('/my-timetable')
@login_required
@student_required
def my_timetable():
    """View student's timetable."""
    student = current_user.student

    timetable = Timetable.query.filter_by(
        department_id=student.department_id,
        year=student.year,
        section=student.section,
        is_active=True
    ).order_by(Timetable.day_of_week, Timetable.period).all()

    # Organize by day
    days = {i: [] for i in range(6)}
    for entry in timetable:
        days[entry.day_of_week].append(entry)

    period_timings = PeriodTiming.query.order_by(PeriodTiming.period).all()

    return render_template('timetable/my_timetable.html',
                           student=student,
                           days=days,
                           period_timings=period_timings)


@bp.route('/staff-schedule')
@login_required
@staff_required
def staff_schedule():
    """View staff's schedule."""
    staff = current_user.staff

    timetable = Timetable.query.filter_by(
        staff_id=staff.id,
        is_active=True
    ).order_by(Timetable.day_of_week, Timetable.period).all()

    # Organize by day
    days = {i: [] for i in range(6)}
    for entry in timetable:
        days[entry.day_of_week].append(entry)

    period_timings = PeriodTiming.query.order_by(PeriodTiming.period).all()

    return render_template('timetable/staff_schedule.html',
                           staff=staff,
                           days=days,
                           period_timings=period_timings)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
@staff_required
def create():
    """Create timetable entry."""
    form = TimetableEntryForm()

    # Populate choices
    departments = Department.query.all()
    form.department_id.choices = [(d.id, d.name) for d in departments]

    subjects = Subject.query.all()
    form.subject_id.choices = [(s.id, f'{s.code} - {s.name}') for s in subjects]

    staff_members = Staff.query.all()
    form.staff_id.choices = [(s.id, s.name) for s in staff_members]

    if form.validate_on_submit():
        # Check for conflict
        existing = Timetable.query.filter_by(
            department_id=form.department_id.data,
            year=form.year.data,
            section=form.section.data,
            day_of_week=form.day_of_week.data,
            period=form.period.data,
            is_active=True
        ).first()

        if existing:
            flash('This slot already has an entry.', 'danger')
        else:
            entry = Timetable(
                department_id=form.department_id.data,
                year=form.year.data,
                section=form.section.data,
                day_of_week=form.day_of_week.data,
                period=form.period.data,
                subject_id=form.subject_id.data,
                staff_id=form.staff_id.data,
                room=form.room.data
            )
            db.session.add(entry)
            db.session.commit()
            flash('Timetable entry added successfully.', 'success')
            return redirect(url_for('timetable.manage'))

    return render_template('timetable/create.html', form=form)


@bp.route('/manage')
@login_required
@staff_required
def manage():
    """Manage timetable."""
    department_id = request.args.get('department_id', type=int)
    year = request.args.get('year', type=int)
    section = request.args.get('section')

    query = Timetable.query.filter_by(is_active=True)

    if department_id:
        query = query.filter_by(department_id=department_id)
    if year:
        query = query.filter_by(year=year)
    if section:
        query = query.filter_by(section=section)

    entries = query.order_by(Timetable.day_of_week, Timetable.period).all()
    departments = Department.query.all()

    return render_template('timetable/manage.html',
                           entries=entries,
                           departments=departments)


@bp.route('/delete/<int:id>')
@login_required
@staff_required
def delete(id):
    """Delete timetable entry."""
    entry = Timetable.query.get_or_404(id)
    entry.is_active = False
    db.session.commit()

    flash('Timetable entry removed.', 'success')
    return redirect(url_for('timetable.manage'))
