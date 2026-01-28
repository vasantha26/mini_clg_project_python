from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import bp
from ...models import FeeStructure, StudentFees, Student, Department
from ...extensions import db
from ...utils.decorators import management_required, student_required
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FloatField, DateField, TextAreaField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, NumberRange, Optional
from datetime import date, datetime


class FeeStructureForm(FlaskForm):
    academic_year = StringField('Academic Year', validators=[DataRequired()],
                                 default=f'{date.today().year}-{str(date.today().year + 1)[-2:]}')
    year = SelectField('Student Year', coerce=int, choices=[
        (0, 'All Years'),
        (1, '1st Year'), (2, '2nd Year'), (3, '3rd Year'), (4, '4th Year')
    ], validators=[DataRequired()])
    department_id = SelectField('Department', coerce=int)
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0)])
    due_date = DateField('Due Date', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Create Fee Structure')


class SingleStudentFeeForm(FlaskForm):
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0)])
    due_date = DateField('Due Date', validators=[DataRequired()], default=date.today)
    description = TextAreaField('Description')
    submit = SubmitField('Add Fee')


class EditStudentFeeForm(FlaskForm):
    amount_due = FloatField('Amount Due', validators=[DataRequired(), NumberRange(min=0)])
    amount_paid = FloatField('Amount Paid', validators=[DataRequired(), NumberRange(min=0)])
    remarks = TextAreaField('Remarks')
    submit = SubmitField('Update Fee')


@bp.route('/structure', methods=['GET', 'POST'])
@login_required
@management_required
def structure():
    """Manage fee structure."""
    form = FeeStructureForm()

    departments = Department.query.all()
    form.department_id.choices = [(0, 'All Departments')] + [
        (d.id, d.name) for d in departments
    ]

    if form.validate_on_submit():
        fee = FeeStructure(
            academic_year=form.academic_year.data,
            year=form.year.data if form.year.data != 0 else None,
            department_id=form.department_id.data if form.department_id.data != 0 else None,
            amount=form.amount.data,
            due_date=form.due_date.data,
            description=form.description.data
        )
        db.session.add(fee)
        db.session.commit()

        flash('Fee structure created successfully.', 'success')
        return redirect(url_for('fees.structure'))

    fee_structures = FeeStructure.query.order_by(FeeStructure.created_at.desc()).all()
    students = Student.query.order_by(Student.roll_number).all()
    return render_template('fees/structure.html', form=form, fee_structures=fee_structures, students=students)


@bp.route('/structure/delete/<int:id>', methods=['POST'])
@login_required
@management_required
def delete_structure(id):
    """Delete fee structure."""
    fee_structure = FeeStructure.query.get_or_404(id)

    # Check if any student fees are linked
    if fee_structure.student_fees.count() > 0:
        flash(f'Cannot delete. {fee_structure.student_fees.count()} students have this fee assigned.', 'danger')
        return redirect(url_for('fees.structure'))

    db.session.delete(fee_structure)
    db.session.commit()
    flash('Fee structure deleted successfully.', 'success')
    return redirect(url_for('fees.structure'))


@bp.route('/upload', methods=['GET', 'POST'])
@login_required
@management_required
def upload():
    """Assign fees to multiple students (bulk)."""
    if request.method == 'POST':
        fee_structure_id = request.form.get('fee_structure_id', type=int)
        fee_structure = FeeStructure.query.get_or_404(fee_structure_id)

        # Get students matching the fee structure criteria
        query = Student.query
        if fee_structure.year:
            query = query.filter_by(year=fee_structure.year)
        if fee_structure.department_id:
            query = query.filter_by(department_id=fee_structure.department_id)

        students = query.all()

        count = 0
        for student in students:
            # Check if fee already assigned
            existing = StudentFees.query.filter_by(
                student_id=student.id,
                fee_structure_id=fee_structure.id
            ).first()

            if not existing:
                student_fee = StudentFees(
                    student_id=student.id,
                    fee_structure_id=fee_structure.id,
                    amount_due=fee_structure.amount
                )
                db.session.add(student_fee)
                count += 1

        db.session.commit()
        flash(f'Fees assigned to {count} students.', 'success')
        return redirect(url_for('fees.student_fees_list'))

    fee_structures = FeeStructure.query.order_by(FeeStructure.created_at.desc()).all()
    return render_template('fees/upload.html', fee_structures=fee_structures)


@bp.route('/add-single', methods=['GET', 'POST'])
@login_required
@management_required
def add_single():
    """Add fee to a single student."""
    form = SingleStudentFeeForm()

    # Populate student dropdown
    students = Student.query.order_by(Student.name).all()
    form.student_id.choices = [(s.id, f"{s.roll_number} - {s.name}") for s in students]

    if form.validate_on_submit():
        student = Student.query.get(form.student_id.data)

        # Create a fee structure for this individual fee
        fee_structure = FeeStructure(
            academic_year=f'{date.today().year}-{str(date.today().year + 1)[-2:]}',
            year=student.year,
            department_id=student.department_id,
            amount=form.amount.data,
            due_date=form.due_date.data,
            description=form.description.data or f"Individual fee for {student.name}"
        )
        db.session.add(fee_structure)
        db.session.flush()

        # Create student fee
        student_fee = StudentFees(
            student_id=student.id,
            fee_structure_id=fee_structure.id,
            amount_due=form.amount.data
        )
        db.session.add(student_fee)
        db.session.commit()

        flash(f'Fee added for {student.name} successfully.', 'success')
        return redirect(url_for('fees.student_fees_list'))

    return render_template('fees/add_single.html', form=form)


@bp.route('/add-multiple', methods=['GET', 'POST'])
@login_required
@management_required
def add_multiple():
    """Add fee to multiple selected students."""
    if request.method == 'POST':
        student_ids = request.form.getlist('student_ids')
        amount = float(request.form.get('amount', 0))
        due_date_str = request.form.get('due_date')
        description = request.form.get('description', '')

        if not student_ids:
            flash('Please select at least one student.', 'danger')
            return redirect(url_for('fees.add_multiple'))

        if amount <= 0:
            flash('Amount must be greater than 0.', 'danger')
            return redirect(url_for('fees.add_multiple'))

        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()

        # Create fee structure
        fee_structure = FeeStructure(
            academic_year=f'{date.today().year}-{str(date.today().year + 1)[-2:]}',
            year=None,
            department_id=None,
            amount=amount,
            due_date=due_date,
            description=description or f"Bulk fee for {len(student_ids)} students"
        )
        db.session.add(fee_structure)
        db.session.flush()

        count = 0
        for student_id in student_ids:
            student_fee = StudentFees(
                student_id=int(student_id),
                fee_structure_id=fee_structure.id,
                amount_due=amount
            )
            db.session.add(student_fee)
            count += 1

        db.session.commit()
        flash(f'Fee added to {count} students successfully.', 'success')
        return redirect(url_for('fees.student_fees_list'))

    # GET request
    students = Student.query.order_by(Student.department_id, Student.name).all()
    departments = Department.query.all()
    today = date.today().strftime('%Y-%m-%d')

    return render_template('fees/add_multiple.html',
                          students=students,
                          departments=departments,
                          today=today)


@bp.route('/student-fees')
@login_required
@management_required
def student_fees_list():
    """View all student fees with filters."""
    department_id = request.args.get('department_id', type=int)
    status = request.args.get('status')

    query = StudentFees.query.join(Student)

    if department_id:
        query = query.filter(Student.department_id == department_id)
    if status:
        query = query.filter(StudentFees.payment_status == status)

    fees = query.order_by(StudentFees.created_at.desc()).all()
    departments = Department.query.all()

    return render_template('fees/student_fees_list.html',
                          fees=fees,
                          departments=departments)


@bp.route('/student-fees/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@management_required
def edit_student_fee(id):
    """Edit student fee."""
    student_fee = StudentFees.query.get_or_404(id)
    form = EditStudentFeeForm(obj=student_fee)

    if form.validate_on_submit():
        student_fee.amount_due = form.amount_due.data
        student_fee.amount_paid = form.amount_paid.data
        student_fee.remarks = form.remarks.data
        student_fee.update_status()

        if student_fee.amount_paid > 0:
            student_fee.payment_date = datetime.utcnow()

        db.session.commit()
        flash('Fee updated successfully.', 'success')
        return redirect(url_for('fees.student_fees_list'))

    return render_template('fees/edit_student_fee.html', form=form, student_fee=student_fee)


@bp.route('/student-fees/delete/<int:id>', methods=['POST'])
@login_required
@management_required
def delete_student_fee(id):
    """Delete student fee."""
    student_fee = StudentFees.query.get_or_404(id)
    student_name = student_fee.student.name

    db.session.delete(student_fee)
    db.session.commit()

    flash(f'Fee for {student_name} deleted successfully.', 'success')
    return redirect(url_for('fees.student_fees_list'))


@bp.route('/student-fees/pay/<int:id>', methods=['POST'])
@login_required
@management_required
def mark_paid(id):
    """Mark fee as fully paid."""
    student_fee = StudentFees.query.get_or_404(id)
    student_fee.amount_paid = student_fee.amount_due
    student_fee.payment_status = 'paid'
    student_fee.payment_date = datetime.utcnow()

    db.session.commit()
    flash(f'Fee for {student_fee.student.name} marked as paid.', 'success')
    return redirect(url_for('fees.student_fees_list'))


@bp.route('/pending-report')
@login_required
@management_required
def pending_report():
    """View pending fees report."""
    pending_fees = StudentFees.query.filter(
        StudentFees.payment_status != 'paid'
    ).order_by(StudentFees.created_at.desc()).all()

    # Group by department
    by_department = {}
    for fee in pending_fees:
        dept_name = fee.student.department.name if fee.student.department else 'Unknown'
        if dept_name not in by_department:
            by_department[dept_name] = {'count': 0, 'total': 0, 'fees': []}
        by_department[dept_name]['count'] += 1
        by_department[dept_name]['total'] += fee.balance
        by_department[dept_name]['fees'].append(fee)

    return render_template('fees/pending_report.html',
                           by_department=by_department,
                           pending_fees=pending_fees)


@bp.route('/my-fees')
@login_required
@student_required
def my_fees():
    """View own fees."""
    student = current_user.student
    fees = StudentFees.query.filter_by(student_id=student.id).order_by(
        StudentFees.created_at.desc()
    ).all()

    total_due = sum(f.amount_due for f in fees)
    total_paid = sum(f.amount_paid for f in fees)
    balance = total_due - total_paid

    return render_template('fees/my_fees.html',
                           student=student,
                           fees=fees,
                           total_due=total_due,
                           total_paid=total_paid,
                           balance=balance)
