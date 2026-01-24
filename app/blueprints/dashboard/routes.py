from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from . import bp
from ...models import (
    Student, Staff, Notification, Notice, AttendanceSummary,
    StudentFees, BookIssue, Complaint, Feedback
)
from ...extensions import db
from sqlalchemy import func


@bp.route('/')
@bp.route('/dashboard')
@login_required
def index():
    # Get unread notification count for navbar
    unread_count = Notification.query.filter_by(
        user_id=current_user.id, is_read=False
    ).count()

    # Get recent notices
    recent_notices = Notice.query.filter_by(is_active=True).order_by(
        Notice.created_at.desc()
    ).limit(5).all()

    if current_user.is_student():
        return render_student_dashboard(unread_count, recent_notices)
    elif current_user.is_staff():
        return render_staff_dashboard(unread_count, recent_notices)
    elif current_user.is_management():
        return render_management_dashboard(unread_count, recent_notices)

    return redirect(url_for('auth.login'))


def render_student_dashboard(unread_count, recent_notices):
    student = current_user.student

    # Get attendance summary
    attendance_summaries = AttendanceSummary.query.filter_by(
        student_id=student.id
    ).all()

    # Calculate average attendance
    avg_attendance = 0
    if attendance_summaries:
        avg_attendance = sum(s.percentage for s in attendance_summaries) / len(attendance_summaries)

    # Get pending fees
    pending_fees = StudentFees.query.filter_by(
        student_id=student.id
    ).filter(StudentFees.payment_status != 'paid').all()

    total_pending = sum(f.balance for f in pending_fees)

    # Get borrowed books
    borrowed_books = BookIssue.query.filter_by(
        student_id=student.id, status='issued'
    ).count()

    # Get complaint status
    pending_complaints = Complaint.query.filter_by(
        submitted_by=student.id
    ).filter(Complaint.status.in_(['pending', 'in_progress'])).count()

    return render_template('dashboard/student.html',
                           student=student,
                           avg_attendance=round(avg_attendance, 1),
                           attendance_summaries=attendance_summaries,
                           total_pending_fees=total_pending,
                           pending_fees=pending_fees,
                           borrowed_books=borrowed_books,
                           pending_complaints=pending_complaints,
                           recent_notices=recent_notices,
                           unread_count=unread_count)


def render_staff_dashboard(unread_count, recent_notices):
    staff = current_user.staff

    # Get today's classes from timetable
    from datetime import datetime
    today = datetime.now().weekday()

    from ...models import Timetable
    today_classes = Timetable.query.filter_by(
        staff_id=staff.id, day_of_week=today, is_active=True
    ).order_by(Timetable.period).all()

    # Get assigned complaints
    assigned_complaints = Complaint.query.filter_by(
        assigned_to=staff.id
    ).filter(Complaint.status.in_(['pending', 'in_progress'])).count()

    # Get feedback received
    recent_feedback = Feedback.query.filter_by(
        target_staff_id=staff.id
    ).order_by(Feedback.created_at.desc()).limit(5).all()

    # Get total students in staff's department
    total_students = Student.query.filter_by(
        department_id=staff.department_id
    ).count()

    return render_template('dashboard/staff.html',
                           staff=staff,
                           today_classes=today_classes,
                           assigned_complaints=assigned_complaints,
                           recent_feedback=recent_feedback,
                           total_students=total_students,
                           recent_notices=recent_notices,
                           unread_count=unread_count)


def render_management_dashboard(unread_count, recent_notices):
    management = current_user.management

    # Get total counts
    total_students = Student.query.count()
    total_staff = Staff.query.count()

    # Get pending complaints
    pending_complaints = Complaint.query.filter(
        Complaint.status.in_(['pending', 'in_progress'])
    ).count()

    # Get total pending fees
    pending_fees_sum = db.session.query(
        func.sum(StudentFees.amount_due - StudentFees.amount_paid)
    ).filter(StudentFees.payment_status != 'paid').scalar() or 0

    # Get recent complaints
    recent_complaints = Complaint.query.order_by(
        Complaint.created_at.desc()
    ).limit(5).all()

    # Get recent feedback
    recent_feedback = Feedback.query.order_by(
        Feedback.created_at.desc()
    ).limit(5).all()

    return render_template('dashboard/management.html',
                           management=management,
                           total_students=total_students,
                           total_staff=total_staff,
                           pending_complaints=pending_complaints,
                           pending_fees_sum=pending_fees_sum,
                           recent_complaints=recent_complaints,
                           recent_feedback=recent_feedback,
                           recent_notices=recent_notices,
                           unread_count=unread_count)
