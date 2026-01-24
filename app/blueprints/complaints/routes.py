from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import bp
from ...models import Complaint, ComplaintResponse, Staff
from ...extensions import db
from ...utils.decorators import student_required, staff_required, management_required
from ...services.notification_service import NotificationService
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length


class ComplaintForm(FlaskForm):
    complaint_type = SelectField('Complaint Type', choices=[
        ('utility', 'Utility (Infrastructure, Facilities)'),
        ('academic', 'Academic (Teaching, Courses)')
    ], validators=[DataRequired()])
    subject = StringField('Subject', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High')
    ], default='normal')
    submit = SubmitField('Submit Complaint')


class ResponseForm(FlaskForm):
    message = TextAreaField('Response', validators=[DataRequired()])
    status = SelectField('Update Status', choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    ])
    submit = SubmitField('Submit Response')


@bp.route('/submit', methods=['GET', 'POST'])
@login_required
@student_required
def submit():
    """Submit a new complaint."""
    form = ComplaintForm()
    student = current_user.student

    if form.validate_on_submit():
        complaint = Complaint(
            complaint_type=form.complaint_type.data,
            subject=form.subject.data,
            description=form.description.data,
            priority=form.priority.data,
            submitted_by=student.id
        )
        db.session.add(complaint)
        db.session.commit()

        # Send notifications
        if complaint.complaint_type == 'utility':
            NotificationService.notify_utility_complaint(complaint)
        else:
            NotificationService.notify_academic_complaint(complaint)

        flash('Complaint submitted successfully.', 'success')
        return redirect(url_for('complaints.my_complaints'))

    return render_template('complaints/submit.html', form=form)


@bp.route('/my-complaints')
@login_required
@student_required
def my_complaints():
    """View own complaints."""
    student = current_user.student
    complaints = Complaint.query.filter_by(submitted_by=student.id).order_by(
        Complaint.created_at.desc()
    ).all()

    return render_template('complaints/my_complaints.html', complaints=complaints)


@bp.route('/detail/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    """View complaint details."""
    complaint = Complaint.query.get_or_404(id)

    # Check permissions
    if current_user.is_student():
        if complaint.submitted_by != current_user.student.id:
            flash('You do not have permission to view this complaint.', 'danger')
            return redirect(url_for('complaints.my_complaints'))

    form = ResponseForm()
    if form.validate_on_submit():
        response = ComplaintResponse(
            complaint_id=complaint.id,
            responder_id=current_user.id,
            message=form.message.data
        )
        complaint.status = form.status.data
        if form.status.data == 'resolved':
            from datetime import datetime
            complaint.resolved_at = datetime.utcnow()

        db.session.add(response)
        db.session.commit()

        flash('Response added successfully.', 'success')
        return redirect(url_for('complaints.detail', id=id))

    responses = complaint.responses.order_by(ComplaintResponse.created_at.desc()).all()
    return render_template('complaints/detail.html',
                           complaint=complaint,
                           form=form,
                           responses=responses)


@bp.route('/assigned')
@login_required
@staff_required
def assigned():
    """View assigned complaints for staff."""
    staff = current_user.staff

    # Get academic complaints for staff's department
    complaints = Complaint.query.filter(
        Complaint.complaint_type == 'academic'
    ).order_by(Complaint.created_at.desc()).all()

    return render_template('complaints/assigned.html', complaints=complaints)


@bp.route('/all')
@login_required
@management_required
def all():
    """View all complaints (management only)."""
    status_filter = request.args.get('status')
    type_filter = request.args.get('type')

    query = Complaint.query

    if status_filter:
        query = query.filter_by(status=status_filter)
    if type_filter:
        query = query.filter_by(complaint_type=type_filter)

    complaints = query.order_by(Complaint.created_at.desc()).all()

    return render_template('complaints/all.html',
                           complaints=complaints,
                           status_filter=status_filter,
                           type_filter=type_filter)
