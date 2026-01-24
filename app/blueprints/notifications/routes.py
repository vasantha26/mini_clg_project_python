from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from . import bp
from ...models import Notification
from ...extensions import db
from ...services.notification_service import NotificationService


@bp.route('/')
@login_required
def index():
    """View all notifications."""
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(
        Notification.created_at.desc()
    ).all()

    unread_count = NotificationService.get_unread_count(current_user.id)

    return render_template('notifications/index.html',
                           notifications=notifications,
                           unread_count=unread_count)


@bp.route('/mark-read/<int:id>')
@login_required
def mark_read(id):
    """Mark a notification as read."""
    NotificationService.mark_as_read(id, current_user.id)
    return redirect(url_for('notifications.index'))


@bp.route('/mark-all-read')
@login_required
def mark_all_read():
    """Mark all notifications as read."""
    NotificationService.mark_all_as_read(current_user.id)
    flash('All notifications marked as read.', 'success')
    return redirect(url_for('notifications.index'))


@bp.route('/unread-count')
@login_required
def unread_count():
    """Get unread notification count (for AJAX)."""
    count = NotificationService.get_unread_count(current_user.id)
    return jsonify({'count': count})
