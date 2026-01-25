from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import bp
from .forms import HODRegistrationForm, StaffRegistrationForm, SubjectForm
from ...models import User, Staff, Department, Subject
from ...extensions import db
from ...utils.decorators import management_required, hod_required, staff_required


# ==================== MANAGEMENT: Create HOD ====================

@bp.route('/hod/list')
@login_required
@management_required
def hod_list():
    """List all HODs (Management only)."""
    # Get all users with role 'hod'
    hods = User.query.filter_by(role='hod').all()
    return render_template('usermanagement/hod_list.html', hods=hods)


@bp.route('/hod/create', methods=['GET', 'POST'])
@login_required
@management_required
def create_hod():
    """Create a new HOD (Management only)."""
    form = HODRegistrationForm()

    departments = Department.query.all()
    form.department_id.choices = [(d.id, d.name) for d in departments]

    if form.validate_on_submit():
        # Check if username or email already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists.', 'danger')
            return render_template('usermanagement/create_hod.html', form=form)

        if User.query.filter_by(email=form.email.data).first():
            flash('Email already exists.', 'danger')
            return render_template('usermanagement/create_hod.html', form=form)

        if Staff.query.filter_by(employee_id=form.employee_id.data).first():
            flash('Employee ID already exists.', 'danger')
            return render_template('usermanagement/create_hod.html', form=form)

        # Create user with role 'hod'
        user = User(
            username=form.username.data,
            email=form.email.data,
            role='hod'
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()

        # Create staff record for HOD
        staff = Staff(
            user_id=user.id,
            employee_id=form.employee_id.data,
            name=form.name.data,
            department_id=form.department_id.data,
            designation=form.designation.data,
            phone=form.phone.data,
            qualification=form.qualification.data,
            joining_date=form.joining_date.data
        )
        db.session.add(staff)
        db.session.flush()

        # Update department with HOD
        department = Department.query.get(form.department_id.data)
        department.hod_id = staff.id

        db.session.commit()

        flash(f'HOD {staff.name} created successfully.', 'success')
        return redirect(url_for('usermanagement.hod_list'))

    return render_template('usermanagement/create_hod.html', form=form)


# ==================== HOD: Create Staff ====================

@bp.route('/staff/list')
@login_required
@hod_required
def staff_list():
    """List all staff in HOD's department."""
    hod_staff = current_user.staff
    staff_members = Staff.query.filter_by(department_id=hod_staff.department_id).all()
    return render_template('usermanagement/staff_list.html', staff_members=staff_members)


@bp.route('/staff/create', methods=['GET', 'POST'])
@login_required
@hod_required
def create_staff():
    """Create a new Staff member (HOD only - in their department)."""
    form = StaffRegistrationForm()
    hod_staff = current_user.staff

    if form.validate_on_submit():
        # Check if username or email already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists.', 'danger')
            return render_template('usermanagement/create_staff.html', form=form, department=hod_staff.department)

        if User.query.filter_by(email=form.email.data).first():
            flash('Email already exists.', 'danger')
            return render_template('usermanagement/create_staff.html', form=form, department=hod_staff.department)

        if Staff.query.filter_by(employee_id=form.employee_id.data).first():
            flash('Employee ID already exists.', 'danger')
            return render_template('usermanagement/create_staff.html', form=form, department=hod_staff.department)

        # Create user with role 'staff'
        user = User(
            username=form.username.data,
            email=form.email.data,
            role='staff'
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()

        # Create staff record (in HOD's department)
        staff = Staff(
            user_id=user.id,
            employee_id=form.employee_id.data,
            name=form.name.data,
            department_id=hod_staff.department_id,  # Same department as HOD
            designation=form.designation.data,
            phone=form.phone.data,
            qualification=form.qualification.data,
            joining_date=form.joining_date.data
        )
        db.session.add(staff)
        db.session.commit()

        flash(f'Staff {staff.name} created successfully.', 'success')
        return redirect(url_for('usermanagement.staff_list'))

    return render_template('usermanagement/create_staff.html', form=form, department=hod_staff.department)


# ==================== STAFF: Create Subject ====================

@bp.route('/subject/list')
@login_required
@staff_required
def subject_list():
    """List all subjects in staff's department."""
    staff = current_user.staff
    subjects = Subject.query.filter_by(department_id=staff.department_id).order_by(Subject.year, Subject.semester).all()
    return render_template('usermanagement/subject_list.html', subjects=subjects)


@bp.route('/subject/create', methods=['GET', 'POST'])
@login_required
@staff_required
def create_subject():
    """Create a new Subject (Staff only - in their department)."""
    form = SubjectForm()
    staff = current_user.staff

    if form.validate_on_submit():
        # Check if subject code already exists
        if Subject.query.filter_by(code=form.code.data).first():
            flash('Subject code already exists.', 'danger')
            return render_template('usermanagement/create_subject.html', form=form, department=staff.department)

        # Create subject (in staff's department)
        subject = Subject(
            code=form.code.data,
            name=form.name.data,
            department_id=staff.department_id,
            year=form.year.data,
            semester=form.semester.data,
            credits=form.credits.data,
            is_lab=form.is_lab.data
        )
        db.session.add(subject)
        db.session.commit()

        flash(f'Subject {subject.name} created successfully.', 'success')
        return redirect(url_for('usermanagement.subject_list'))

    return render_template('usermanagement/create_subject.html', form=form, department=staff.department)
