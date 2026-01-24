from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user


def role_required(*roles):
    """
    Decorator to restrict access to specific roles.
    Usage: @role_required('staff', 'management')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            if current_user.role not in roles:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('dashboard.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def student_required(f):
    """Decorator for student-only routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_student():
            flash('This page is only accessible to students.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function


def staff_required(f):
    """Decorator for staff-only routes (includes HOD)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_staff():
            flash('This page is only accessible to staff members.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function


def management_required(f):
    """Decorator for management-only routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_management():
            flash('This page is only accessible to management.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function


def hod_required(f):
    """Decorator for HOD-only routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_hod():
            flash('This page is only accessible to HODs.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function
