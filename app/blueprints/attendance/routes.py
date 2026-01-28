from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import bp
from .forms import AttendanceSessionForm
from ...models import (
    AttendanceSession, AttendanceRecord, AttendanceSummary,
    Student, Subject, Department
)
from ...extensions import db
from ...utils.decorators import staff_required, student_required
from ...services.notification_service import NotificationService


@bp.route('/take', methods=['GET', 'POST'])
@login_required
@staff_required
def take():
    """Create attendance session."""
    form = AttendanceSessionForm()
    staff = current_user.staff

    # Populate subject choices with all subjects
    all_subjects = Subject.query.all()
    form.subject_id.choices = [
        (s.id, f'{s.code} - {s.name}') for s in all_subjects
    ]

    # Get filter parameters for student list
    filter_year = request.args.get('year', type=int)
    filter_section = request.args.get('section', '')

    # Get students based on filters
    students = []
    if filter_year and filter_section:
        students = Student.query.filter_by(
            department_id=staff.department_id,
            year=filter_year,
            section=filter_section
        ).order_by(Student.roll_number).all()
        # Pre-fill form with filter values
        form.year.data = filter_year
        form.section.data = filter_section

    if form.validate_on_submit():
        # Check if session already exists
        existing = AttendanceSession.query.filter_by(
            subject_id=form.subject_id.data,
            date=form.date.data,
            period=form.period.data,
            section=form.section.data,
            department_id=staff.department_id
        ).first()

        if existing:
            flash('Attendance session already exists for this slot.', 'warning')
            return redirect(url_for('attendance.mark', session_id=existing.id))

        session = AttendanceSession(
            subject_id=form.subject_id.data,
            staff_id=staff.id,
            date=form.date.data,
            period=form.period.data,
            year=form.year.data,
            section=form.section.data,
            department_id=staff.department_id
        )
        db.session.add(session)
        db.session.commit()

        flash('Attendance session created successfully.', 'success')
        return redirect(url_for('attendance.mark', session_id=session.id))

    return render_template('attendance/take.html', form=form, students=students)


@bp.route('/mark/<int:session_id>', methods=['GET', 'POST'])
@login_required
@staff_required
def mark(session_id):
    """Mark attendance for a session."""
    session = AttendanceSession.query.get_or_404(session_id)
    staff = current_user.staff

    # Verify staff owns this session
    if session.staff_id != staff.id:
        flash('You do not have permission to mark this attendance.', 'danger')
        return redirect(url_for('attendance.take'))

    # Get students for this session
    students = Student.query.filter_by(
        department_id=session.department_id,
        year=session.year,
        section=session.section
    ).order_by(Student.roll_number).all()

    if request.method == 'POST':
        # Get present student IDs from form
        present_ids = request.form.getlist('present')

        for student in students:
            # Check if record already exists
            record = AttendanceRecord.query.filter_by(
                session_id=session.id,
                student_id=student.id
            ).first()

            is_present = str(student.id) in present_ids

            if record:
                record.is_present = is_present
            else:
                record = AttendanceRecord(
                    session_id=session.id,
                    student_id=student.id,
                    is_present=is_present
                )
                db.session.add(record)

            # Update attendance summary
            update_attendance_summary(student.id, session.subject_id)

        db.session.commit()
        flash('Attendance marked successfully.', 'success')
        return redirect(url_for('attendance.reports'))

    # Get existing records
    existing_records = {r.student_id: r.is_present for r in session.records}

    return render_template('attendance/mark.html',
                           session=session,
                           students=students,
                           existing_records=existing_records)


def update_attendance_summary(student_id, subject_id):
    """Update attendance summary for a student-subject pair."""
    # Get all attendance records for this student-subject
    records = AttendanceRecord.query.join(AttendanceSession).filter(
        AttendanceRecord.student_id == student_id,
        AttendanceSession.subject_id == subject_id
    ).all()

    total_classes = len(records)
    attended = sum(1 for r in records if r.is_present)
    percentage = (attended / total_classes * 100) if total_classes > 0 else 0

    # Get or create summary
    summary = AttendanceSummary.query.filter_by(
        student_id=student_id,
        subject_id=subject_id
    ).first()

    if not summary:
        summary = AttendanceSummary(
            student_id=student_id,
            subject_id=subject_id
        )
        db.session.add(summary)

    summary.total_classes = total_classes
    summary.attended = attended
    summary.percentage = percentage

    # Check if attendance is below 75% and notify
    if percentage < 75 and total_classes >= 5:  # Only notify after 5 classes
        student = Student.query.get(student_id)
        subject = Subject.query.get(subject_id)
        NotificationService.notify_low_attendance(student, subject, percentage)


@bp.route('/reports')
@login_required
@staff_required
def reports():
    """View attendance list."""
    staff = current_user.staff
    sessions = AttendanceSession.query.filter_by(staff_id=staff.id).order_by(AttendanceSession.date.desc()).all()
    return render_template('attendance/reports.html', sessions=sessions)


@bp.route('/my-attendance')
@login_required
@student_required
def my_attendance():
    """View own attendance."""
    student = current_user.student

    # Get attendance summaries
    summaries = AttendanceSummary.query.filter_by(
        student_id=student.id
    ).all()

    # Get detailed records by subject
    subjects_data = []
    for summary in summaries:
        records = AttendanceRecord.query.join(AttendanceSession).filter(
            AttendanceRecord.student_id == student.id,
            AttendanceSession.subject_id == summary.subject_id
        ).order_by(AttendanceSession.date.desc()).all()

        subjects_data.append({
            'summary': summary,
            'records': records[:10]  # Last 10 records
        })

    return render_template('attendance/my_attendance.html',
                           student=student,
                           subjects_data=subjects_data)
