from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from . import bp
from .forms import LoginForm
from ...models import User


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('auth.login'))

        if user.role != form.role.data:
            flash('Invalid role selected for this account.', 'danger')
            return redirect(url_for('auth.login'))

        if not user.is_active:
            flash('Your account has been deactivated. Please contact administration.', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user)
        flash(f'Welcome back, {user.get_display_name()}!', 'success')

        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('dashboard.index'))

    return render_template('auth/login.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
