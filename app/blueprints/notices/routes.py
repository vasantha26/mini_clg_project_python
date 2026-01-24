from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import bp
from ...models import Notice, Department
from ...extensions import db
from ...utils.decorators import management_required
from ...services.notification_service import NotificationService
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, Length
from datetime import datetime


class NoticeForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('general', 'General'),
        ('academic', 'Academic'),
        ('event', 'Event'),
        ('exam', 'Examination'),
        ('holiday', 'Holiday')
    ], validators=[DataRequired()])
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], default='normal')
    target_audience = SelectField('Target Audience', choices=[
        ('all', 'Everyone'),
        ('students', 'All Students'),
        ('staff', 'All Staff')
    ])
    department_id = SelectField('Department', coerce=int)
    expiry_date = DateTimeField('Expiry Date (Optional)', format='%Y-%m-%dT%H:%M')
    submit = SubmitField('Post Notice')


@bp.route('/')
@login_required
def index():
    """View notices."""
    category = request.args.get('category')

    query = Notice.query.filter_by(is_active=True)
    if category:
        query = query.filter_by(category=category)

    notices = query.order_by(Notice.priority.desc(), Notice.created_at.desc()).all()

    return render_template('notices/index.html', notices=notices, category=category)


@bp.route('/detail/<int:id>')
@login_required
def detail(id):
    """View notice details."""
    notice = Notice.query.get_or_404(id)
    return render_template('notices/detail.html', notice=notice)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
@management_required
def create():
    """Create a new notice."""
    form = NoticeForm()

    departments = Department.query.all()
    form.department_id.choices = [(0, 'All Departments')] + [
        (d.id, d.name) for d in departments
    ]

    if form.validate_on_submit():
        notice = Notice(
            title=form.title.data,
            content=form.content.data,
            category=form.category.data,
            priority=form.priority.data,
            target_audience=form.target_audience.data,
            department_id=form.department_id.data if form.department_id.data != 0 else None,
            posted_by=current_user.management.id,
            expiry_date=form.expiry_date.data
        )
        db.session.add(notice)
        db.session.commit()

        # Notify all users
        NotificationService.notify_new_notice(notice)

        flash('Notice posted successfully.', 'success')
        return redirect(url_for('notices.manage'))

    return render_template('notices/create.html', form=form)


@bp.route('/manage')
@login_required
@management_required
def manage():
    """Manage notices."""
    notices = Notice.query.order_by(Notice.created_at.desc()).all()
    return render_template('notices/manage.html', notices=notices)


@bp.route('/toggle/<int:id>')
@login_required
@management_required
def toggle(id):
    """Toggle notice active status."""
    notice = Notice.query.get_or_404(id)
    notice.is_active = not notice.is_active
    db.session.commit()

    status = 'activated' if notice.is_active else 'deactivated'
    flash(f'Notice {status} successfully.', 'success')
    return redirect(url_for('notices.manage'))


@bp.route('/delete/<int:id>')
@login_required
@management_required
def delete(id):
    """Delete a notice."""
    notice = Notice.query.get_or_404(id)
    db.session.delete(notice)
    db.session.commit()

    flash('Notice deleted successfully.', 'success')
    return redirect(url_for('notices.manage'))
