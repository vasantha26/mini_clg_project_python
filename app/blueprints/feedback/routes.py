from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import bp
from ...models import Feedback, Staff, Subject
from ...extensions import db
from ...utils.decorators import student_required, staff_required, management_required
from ...services.notification_service import NotificationService
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class FeedbackForm(FlaskForm):
    feedback_type = SelectField('Feedback Type', choices=[
        ('general', 'General Feedback'),
        ('staff', 'Staff Feedback')
    ], validators=[DataRequired()])
    target_staff_id = SelectField('Staff Member', coerce=int)
    subject_id = SelectField('Subject', coerce=int)
    content = TextAreaField('Feedback', validators=[DataRequired()])
    rating = IntegerField('Rating', validators=[DataRequired(), NumberRange(min=1, max=5)])
    is_anonymous = BooleanField('Submit Anonymously')
    submit = SubmitField('Submit Feedback')


@bp.route('/submit', methods=['GET', 'POST'])
@login_required
@student_required
def submit():
    """Submit feedback."""
    form = FeedbackForm()
    student = current_user.student

    # Populate staff choices
    staff_members = Staff.query.all()
    form.target_staff_id.choices = [(0, 'Select Staff (Optional)')] + [
        (s.id, s.name) for s in staff_members
    ]

    # Populate subject choices - show all subjects
    subjects = Subject.query.all()
    form.subject_id.choices = [(0, 'Select Subject (Optional)')] + [
        (s.id, f'{s.code} - {s.name}') for s in subjects
    ]

    if form.validate_on_submit():
        feedback = Feedback(
            feedback_type=form.feedback_type.data,
            content=form.content.data,
            rating=form.rating.data,
            is_anonymous=form.is_anonymous.data,
            submitted_by=student.id,
            target_staff_id=form.target_staff_id.data if form.target_staff_id.data != 0 else None,
            subject_id=form.subject_id.data if form.subject_id.data != 0 else None
        )
        db.session.add(feedback)
        db.session.commit()

        # Send notifications
        if feedback.feedback_type == 'staff' and feedback.target_staff_id:
            NotificationService.notify_staff_feedback(feedback)
        else:
            NotificationService.notify_general_feedback(feedback)

        flash('Feedback submitted successfully.', 'success')
        return redirect(url_for('feedback.my_feedback'))

    return render_template('feedback/submit.html', form=form)


@bp.route('/my-feedback')
@login_required
@student_required
def my_feedback():
    """View own feedback."""
    student = current_user.student
    feedbacks = Feedback.query.filter_by(submitted_by=student.id).order_by(
        Feedback.created_at.desc()
    ).all()

    return render_template('feedback/my_feedback.html', feedbacks=feedbacks)


@bp.route('/staff-feedback')
@login_required
@staff_required
def staff_feedback():
    """View feedback received by staff."""
    staff = current_user.staff
    feedbacks = Feedback.query.filter_by(target_staff_id=staff.id).order_by(
        Feedback.created_at.desc()
    ).all()

    # Calculate average rating
    if feedbacks:
        avg_rating = sum(f.rating for f in feedbacks) / len(feedbacks)
    else:
        avg_rating = 0

    return render_template('feedback/staff_feedback.html',
                           feedbacks=feedbacks,
                           avg_rating=avg_rating)


@bp.route('/all')
@login_required
@management_required
def all():
    """View all feedback (management only)."""
    type_filter = request.args.get('type')

    query = Feedback.query
    if type_filter:
        query = query.filter_by(feedback_type=type_filter)

    feedbacks = query.order_by(Feedback.created_at.desc()).all()

    return render_template('feedback/all.html',
                           feedbacks=feedbacks,
                           type_filter=type_filter)
