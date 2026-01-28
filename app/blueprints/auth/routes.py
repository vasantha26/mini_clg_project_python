from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from . import bp
from .forms import StudentLoginForm, StaffLoginForm
from ...models import User, Student


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    student_form = StudentLoginForm()
    staff_form = StaffLoginForm()

    # Check which form was submitted
    login_type = request.form.get('login_type', 'student')

    if request.method == 'POST':
        if login_type == 'student' and student_form.validate_on_submit():
            # Student login with roll number and DOB
            student = Student.query.filter_by(roll_number=student_form.roll_number.data).first()

            if student is None:
                flash('Invalid roll number.', 'danger')
                return render_template('auth/login.html', student_form=student_form, staff_form=staff_form, active_tab='student')

            if student.date_of_birth != student_form.date_of_birth.data:
                flash('Invalid date of birth.', 'danger')
                return render_template('auth/login.html', student_form=student_form, staff_form=staff_form, active_tab='student')

            user = student.user
            if not user.is_active:
                flash('Your account has been deactivated. Please contact administration.', 'danger')
                return render_template('auth/login.html', student_form=student_form, staff_form=staff_form, active_tab='student')

            login_user(user)
            flash(f'Welcome back, {user.get_display_name()}!', 'success')

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard.index'))

        elif login_type == 'staff' and staff_form.validate_on_submit():
            # Staff/HOD/Management login with username and password
            user = User.query.filter_by(username=staff_form.username.data).first()

            if user is None or not user.check_password(staff_form.password.data):
                flash('Invalid username or password.', 'danger')
                return render_template('auth/login.html', student_form=student_form, staff_form=staff_form, active_tab='staff')

            if user.role != staff_form.role.data:
                flash('Invalid role selected for this account.', 'danger')
                return render_template('auth/login.html', student_form=student_form, staff_form=staff_form, active_tab='staff')

            if not user.is_active:
                flash('Your account has been deactivated. Please contact administration.', 'danger')
                return render_template('auth/login.html', student_form=student_form, staff_form=staff_form, active_tab='staff')

            login_user(user)
            flash(f'Welcome back, {user.get_display_name()}!', 'success')

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard.index'))

    return render_template('auth/login.html', student_form=student_form, staff_form=staff_form, active_tab='student')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
