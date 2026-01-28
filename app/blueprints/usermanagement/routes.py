from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import bp
from .forms import HODRegistrationForm, HODEditForm, StaffRegistrationForm, StaffEditForm, SubjectForm, DepartmentForm
from ...models import User, Staff, Department, Subject, Student, StaffAssignment
from ...extensions import db
from ...utils.decorators import management_required, hod_required, staff_required
from datetime import date


# ==================== MANAGEMENT: HOD CRUD ====================

@bp.route('/hod/list')
@login_required
@management_required
def hod_list():
    """List all HODs (Management only)."""
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
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists.', 'danger')
            return render_template('usermanagement/create_hod.html', form=form)

        if User.query.filter_by(email=form.email.data).first():
            flash('Email already exists.', 'danger')
            return render_template('usermanagement/create_hod.html', form=form)

        if Staff.query.filter_by(employee_id=form.employee_id.data).first():
            flash('Employee ID already exists.', 'danger')
            return render_template('usermanagement/create_hod.html', form=form)

        user = User(
            username=form.username.data,
            email=form.email.data,
            role='hod'
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()

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

        department = Department.query.get(form.department_id.data)
        department.hod_id = staff.id
        db.session.commit()

        flash(f'HOD {staff.name} created successfully.', 'success')
        return redirect(url_for('usermanagement.hod_list'))

    return render_template('usermanagement/create_hod.html', form=form)


@bp.route('/hod/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@management_required
def edit_hod(id):
    """Edit HOD (Management only)."""
    user = User.query.get_or_404(id)
    if user.role != 'hod':
        flash('Invalid HOD.', 'danger')
        return redirect(url_for('usermanagement.hod_list'))

    staff = user.staff
    form = HODEditForm(obj=staff)
    departments = Department.query.all()
    form.department_id.choices = [(d.id, d.name) for d in departments]

    if request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.department_id.data = staff.department_id

    if form.validate_on_submit():
        # Check username uniqueness
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user and existing_user.id != user.id:
            flash('Username already exists.', 'danger')
            return render_template('usermanagement/edit_hod.html', form=form, hod=user)

        # Check email uniqueness
        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_email and existing_email.id != user.id:
            flash('Email already exists.', 'danger')
            return render_template('usermanagement/edit_hod.html', form=form, hod=user)

        # Check employee_id uniqueness
        existing_emp = Staff.query.filter_by(employee_id=form.employee_id.data).first()
        if existing_emp and existing_emp.id != staff.id:
            flash('Employee ID already exists.', 'danger')
            return render_template('usermanagement/edit_hod.html', form=form, hod=user)

        # Update user
        user.username = form.username.data
        user.email = form.email.data
        if form.password.data:
            user.set_password(form.password.data)

        # Update old department HOD if department changed
        if staff.department_id != form.department_id.data:
            old_dept = Department.query.get(staff.department_id)
            if old_dept and old_dept.hod_id == staff.id:
                old_dept.hod_id = None

            # Set new department HOD
            new_dept = Department.query.get(form.department_id.data)
            new_dept.hod_id = staff.id

        # Update staff
        staff.employee_id = form.employee_id.data
        staff.name = form.name.data
        staff.department_id = form.department_id.data
        staff.designation = form.designation.data
        staff.phone = form.phone.data
        staff.qualification = form.qualification.data
        staff.joining_date = form.joining_date.data

        db.session.commit()
        flash(f'HOD {staff.name} updated successfully.', 'success')
        return redirect(url_for('usermanagement.hod_list'))

    return render_template('usermanagement/edit_hod.html', form=form, hod=user)


@bp.route('/hod/delete/<int:id>', methods=['POST'])
@login_required
@management_required
def delete_hod(id):
    """Delete HOD (Management only)."""
    user = User.query.get_or_404(id)
    if user.role != 'hod':
        flash('Invalid HOD.', 'danger')
        return redirect(url_for('usermanagement.hod_list'))

    staff = user.staff
    name = staff.name

    # Remove HOD from department
    dept = Department.query.filter_by(hod_id=staff.id).first()
    if dept:
        dept.hod_id = None

    db.session.delete(user)
    db.session.commit()

    flash(f'HOD {name} deleted successfully.', 'success')
    return redirect(url_for('usermanagement.hod_list'))


# ==================== HOD: Staff CRUD ====================

@bp.route('/staff/list')
@login_required
@hod_required
def staff_list():
    """List all staff in HOD's department."""
    hod_staff = current_user.staff
    staff_members = Staff.query.filter_by(department_id=hod_staff.department_id).all()
    # Filter out HODs from the list
    staff_members = [s for s in staff_members if s.user.role == 'staff']
    return render_template('usermanagement/staff_list.html', staff_members=staff_members)


@bp.route('/staff/create', methods=['GET', 'POST'])
@login_required
@hod_required
def create_staff():
    """Create a new Staff member (HOD only)."""
    form = StaffRegistrationForm()
    hod_staff = current_user.staff

    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists.', 'danger')
            return render_template('usermanagement/create_staff.html', form=form, department=hod_staff.department)

        if User.query.filter_by(email=form.email.data).first():
            flash('Email already exists.', 'danger')
            return render_template('usermanagement/create_staff.html', form=form, department=hod_staff.department)

        if Staff.query.filter_by(employee_id=form.employee_id.data).first():
            flash('Employee ID already exists.', 'danger')
            return render_template('usermanagement/create_staff.html', form=form, department=hod_staff.department)

        user = User(
            username=form.username.data,
            email=form.email.data,
            role='staff'
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()

        staff = Staff(
            user_id=user.id,
            employee_id=form.employee_id.data,
            name=form.name.data,
            department_id=hod_staff.department_id,
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


@bp.route('/staff/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@hod_required
def edit_staff(id):
    """Edit Staff member (HOD only)."""
    user = User.query.get_or_404(id)
    hod_staff = current_user.staff

    if user.role != 'staff':
        flash('Invalid staff member.', 'danger')
        return redirect(url_for('usermanagement.staff_list'))

    staff = user.staff
    # Ensure staff is in HOD's department
    if staff.department_id != hod_staff.department_id:
        flash('You can only edit staff in your department.', 'danger')
        return redirect(url_for('usermanagement.staff_list'))

    form = StaffEditForm(obj=staff)

    if request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email

    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user and existing_user.id != user.id:
            flash('Username already exists.', 'danger')
            return render_template('usermanagement/edit_staff.html', form=form, staff_member=user, department=hod_staff.department)

        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_email and existing_email.id != user.id:
            flash('Email already exists.', 'danger')
            return render_template('usermanagement/edit_staff.html', form=form, staff_member=user, department=hod_staff.department)

        existing_emp = Staff.query.filter_by(employee_id=form.employee_id.data).first()
        if existing_emp and existing_emp.id != staff.id:
            flash('Employee ID already exists.', 'danger')
            return render_template('usermanagement/edit_staff.html', form=form, staff_member=user, department=hod_staff.department)

        user.username = form.username.data
        user.email = form.email.data
        if form.password.data:
            user.set_password(form.password.data)

        staff.employee_id = form.employee_id.data
        staff.name = form.name.data
        staff.designation = form.designation.data
        staff.phone = form.phone.data
        staff.qualification = form.qualification.data
        staff.joining_date = form.joining_date.data

        db.session.commit()
        flash(f'Staff {staff.name} updated successfully.', 'success')
        return redirect(url_for('usermanagement.staff_list'))

    return render_template('usermanagement/edit_staff.html', form=form, staff_member=user, department=hod_staff.department)


@bp.route('/staff/delete/<int:id>', methods=['POST'])
@login_required
@hod_required
def delete_staff(id):
    """Delete Staff member (HOD only)."""
    user = User.query.get_or_404(id)
    hod_staff = current_user.staff

    if user.role != 'staff':
        flash('Invalid staff member.', 'danger')
        return redirect(url_for('usermanagement.staff_list'))

    staff = user.staff
    if staff.department_id != hod_staff.department_id:
        flash('You can only delete staff in your department.', 'danger')
        return redirect(url_for('usermanagement.staff_list'))

    name = staff.name
    db.session.delete(user)
    db.session.commit()

    flash(f'Staff {name} deleted successfully.', 'success')
    return redirect(url_for('usermanagement.staff_list'))


# ==================== STAFF: Subject CRUD ====================

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
    """Create a new Subject (Staff only)."""
    form = SubjectForm()
    staff = current_user.staff

    if form.validate_on_submit():
        if Subject.query.filter_by(code=form.code.data).first():
            flash('Subject code already exists.', 'danger')
            return render_template('usermanagement/create_subject.html', form=form, department=staff.department)

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


@bp.route('/subject/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@staff_required
def edit_subject(id):
    """Edit Subject (Staff only)."""
    subject = Subject.query.get_or_404(id)
    staff = current_user.staff

    if subject.department_id != staff.department_id:
        flash('You can only edit subjects in your department.', 'danger')
        return redirect(url_for('usermanagement.subject_list'))

    form = SubjectForm(obj=subject)

    if form.validate_on_submit():
        existing = Subject.query.filter_by(code=form.code.data).first()
        if existing and existing.id != subject.id:
            flash('Subject code already exists.', 'danger')
            return render_template('usermanagement/edit_subject.html', form=form, subject=subject, department=staff.department)

        subject.code = form.code.data
        subject.name = form.name.data
        subject.year = form.year.data
        subject.semester = form.semester.data
        subject.credits = form.credits.data
        subject.is_lab = form.is_lab.data

        db.session.commit()
        flash(f'Subject {subject.name} updated successfully.', 'success')
        return redirect(url_for('usermanagement.subject_list'))

    return render_template('usermanagement/edit_subject.html', form=form, subject=subject, department=staff.department)


@bp.route('/subject/delete/<int:id>', methods=['POST'])
@login_required
@staff_required
def delete_subject(id):
    """Delete Subject (Staff only)."""
    subject = Subject.query.get_or_404(id)
    staff = current_user.staff

    if subject.department_id != staff.department_id:
        flash('You can only delete subjects in your department.', 'danger')
        return redirect(url_for('usermanagement.subject_list'))

    name = subject.name
    db.session.delete(subject)
    db.session.commit()

    flash(f'Subject {name} deleted successfully.', 'success')
    return redirect(url_for('usermanagement.subject_list'))


# ==================== MANAGEMENT: Department CRUD ====================

@bp.route('/department/list')
@login_required
@management_required
def department_list():
    """List all departments (Management only)."""
    departments = Department.query.order_by(Department.name).all()
    return render_template('usermanagement/department_list.html', departments=departments)


@bp.route('/department/create', methods=['GET', 'POST'])
@login_required
@management_required
def create_department():
    """Create a new Department (Management only)."""
    form = DepartmentForm()

    if form.validate_on_submit():
        if Department.query.filter_by(code=form.code.data).first():
            flash('Department code already exists.', 'danger')
            return render_template('usermanagement/create_department.html', form=form)

        department = Department(
            code=form.code.data.upper(),
            name=form.name.data
        )
        db.session.add(department)
        db.session.commit()

        flash(f'Department {department.name} created successfully.', 'success')
        return redirect(url_for('usermanagement.department_list'))

    return render_template('usermanagement/create_department.html', form=form)


@bp.route('/department/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@management_required
def edit_department(id):
    """Edit Department (Management only)."""
    department = Department.query.get_or_404(id)
    form = DepartmentForm(obj=department)

    if form.validate_on_submit():
        existing = Department.query.filter_by(code=form.code.data).first()
        if existing and existing.id != department.id:
            flash('Department code already exists.', 'danger')
            return render_template('usermanagement/edit_department.html', form=form, department=department)

        department.code = form.code.data.upper()
        department.name = form.name.data
        db.session.commit()

        flash(f'Department {department.name} updated successfully.', 'success')
        return redirect(url_for('usermanagement.department_list'))

    return render_template('usermanagement/edit_department.html', form=form, department=department)


@bp.route('/department/delete/<int:id>', methods=['POST'])
@login_required
@management_required
def delete_department(id):
    """Delete Department (Management only)."""
    department = Department.query.get_or_404(id)

    # Check if department has students, staff, or subjects
    if department.students.count() > 0:
        flash(f'Cannot delete department. It has {department.students.count()} students.', 'danger')
        return redirect(url_for('usermanagement.department_list'))

    if department.staff_members.count() > 0:
        flash(f'Cannot delete department. It has {department.staff_members.count()} staff members.', 'danger')
        return redirect(url_for('usermanagement.department_list'))

    name = department.name
    db.session.delete(department)
    db.session.commit()

    flash(f'Department {name} deleted successfully.', 'success')
    return redirect(url_for('usermanagement.department_list'))


# ==================== HOD: Staff Assignment ====================

@bp.route('/assignment/list')
@login_required
@hod_required
def assignment_list():
    """List all staff assignments in HOD's department."""
    hod_staff = current_user.staff
    assignments = StaffAssignment.query.filter_by(department_id=hod_staff.department_id).order_by(StaffAssignment.created_at.desc()).all()
    return render_template('usermanagement/assignment_list.html', assignments=assignments)


@bp.route('/assignment/create', methods=['GET', 'POST'])
@login_required
@hod_required
def create_assignment():
    """Create a new staff assignment (HOD only)."""
    hod_staff = current_user.staff

    if request.method == 'POST':
        staff_id = request.form.get('staff_id', type=int)
        subject_id = request.form.get('subject_id', type=int)
        year = request.form.get('year', type=int)
        assigned_date_str = request.form.get('assigned_date')

        if not all([staff_id, subject_id, year, assigned_date_str]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('usermanagement.create_assignment'))

        # Check if assignment already exists
        existing = StaffAssignment.query.filter_by(
            staff_id=staff_id,
            subject_id=subject_id,
            year=year
        ).first()
        if existing:
            flash('This assignment already exists.', 'danger')
            return redirect(url_for('usermanagement.create_assignment'))

        from datetime import datetime
        assigned_date = datetime.strptime(assigned_date_str, '%Y-%m-%d').date()

        assignment = StaffAssignment(
            staff_id=staff_id,
            subject_id=subject_id,
            year=year,
            assigned_date=assigned_date,
            department_id=hod_staff.department_id
        )
        db.session.add(assignment)
        db.session.commit()

        flash('Staff assignment created successfully.', 'success')
        return redirect(url_for('usermanagement.assignment_list'))

    # GET request
    staff_members = Staff.query.filter_by(department_id=hod_staff.department_id).all()
    staff_members = [s for s in staff_members if s.user.role == 'staff']
    subjects = Subject.query.filter_by(department_id=hod_staff.department_id).order_by(Subject.year, Subject.name).all()
    today = date.today().strftime('%Y-%m-%d')

    return render_template('usermanagement/create_assignment.html',
                          staff_members=staff_members,
                          subjects=subjects,
                          today=today)


@bp.route('/assignment/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@hod_required
def edit_assignment(id):
    """Edit staff assignment (HOD only)."""
    assignment = StaffAssignment.query.get_or_404(id)
    hod_staff = current_user.staff

    if assignment.department_id != hod_staff.department_id:
        flash('You can only edit assignments in your department.', 'danger')
        return redirect(url_for('usermanagement.assignment_list'))

    if request.method == 'POST':
        staff_id = request.form.get('staff_id', type=int)
        subject_id = request.form.get('subject_id', type=int)
        year = request.form.get('year', type=int)
        assigned_date_str = request.form.get('assigned_date')

        if not all([staff_id, subject_id, year, assigned_date_str]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('usermanagement.edit_assignment', id=id))

        # Check if assignment already exists (excluding current)
        existing = StaffAssignment.query.filter_by(
            staff_id=staff_id,
            subject_id=subject_id,
            year=year
        ).first()
        if existing and existing.id != assignment.id:
            flash('This assignment already exists.', 'danger')
            return redirect(url_for('usermanagement.edit_assignment', id=id))

        from datetime import datetime
        assigned_date = datetime.strptime(assigned_date_str, '%Y-%m-%d').date()

        assignment.staff_id = staff_id
        assignment.subject_id = subject_id
        assignment.year = year
        assignment.assigned_date = assigned_date

        db.session.commit()
        flash('Staff assignment updated successfully.', 'success')
        return redirect(url_for('usermanagement.assignment_list'))

    # GET request
    staff_members = Staff.query.filter_by(department_id=hod_staff.department_id).all()
    staff_members = [s for s in staff_members if s.user.role == 'staff']
    subjects = Subject.query.filter_by(department_id=hod_staff.department_id).order_by(Subject.year, Subject.name).all()

    return render_template('usermanagement/edit_assignment.html',
                          assignment=assignment,
                          staff_members=staff_members,
                          subjects=subjects)


@bp.route('/assignment/delete/<int:id>', methods=['POST'])
@login_required
@hod_required
def delete_assignment(id):
    """Delete staff assignment (HOD only)."""
    assignment = StaffAssignment.query.get_or_404(id)
    hod_staff = current_user.staff

    if assignment.department_id != hod_staff.department_id:
        flash('You can only delete assignments in your department.', 'danger')
        return redirect(url_for('usermanagement.assignment_list'))

    db.session.delete(assignment)
    db.session.commit()

    flash('Staff assignment deleted successfully.', 'success')
    return redirect(url_for('usermanagement.assignment_list'))


# ==================== HOD: Student List ====================

@bp.route('/hod/students')
@login_required
@hod_required
def hod_student_list():
    """List all students in HOD's department."""
    hod_staff = current_user.staff
    students = Student.query.filter_by(department_id=hod_staff.department_id).order_by(Student.roll_number).all()
    return render_template('usermanagement/hod_student_list.html', students=students)
