from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import bp
from ...models import FeeStructure, StudentFees, Student, Department
from ...extensions import db
from ...utils.decorators import management_required, student_required
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FloatField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from datetime import date


class FeeStructureForm(FlaskForm):
    academic_year = StringField('Academic Year', validators=[DataRequired()],
                                 default=f'{date.today().year}-{str(date.today().year + 1)[-2:]}')
    year = SelectField('Student Year', coerce=int, choices=[
        (1, '1st Year'), (2, '2nd Year'), (3, '3rd Year'), (4, '4th Year')
    ], validators=[DataRequired()])
    department_id = SelectField('Department', coerce=int)
    fee_type = SelectField('Fee Type', choices=[
        ('tuition', 'Tuition Fee'),
        ('exam', 'Examination Fee'),
        ('library', 'Library Fee'),
        ('lab', 'Laboratory Fee'),
        ('sports', 'Sports Fee'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0)])
    due_date = DateField('Due Date', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Create Fee Structure')


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
            year=form.year.data,
            department_id=form.department_id.data if form.department_id.data != 0 else None,
            fee_type=form.fee_type.data,
            amount=form.amount.data,
            due_date=form.due_date.data,
            description=form.description.data
        )
        db.session.add(fee)
        db.session.commit()

        flash('Fee structure created successfully.', 'success')
        return redirect(url_for('fees.structure'))

    fee_structures = FeeStructure.query.order_by(FeeStructure.created_at.desc()).all()
    return render_template('fees/structure.html', form=form, fee_structures=fee_structures)


@bp.route('/upload', methods=['GET', 'POST'])
@login_required
@management_required
def upload():
    """Assign fees to students."""
    if request.method == 'POST':
        fee_structure_id = request.form.get('fee_structure_id', type=int)
        fee_structure = FeeStructure.query.get_or_404(fee_structure_id)

        # Get students matching the fee structure criteria
        query = Student.query.filter_by(year=fee_structure.year)
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
        return redirect(url_for('fees.structure'))

    fee_structures = FeeStructure.query.order_by(FeeStructure.created_at.desc()).all()
    return render_template('fees/upload.html', fee_structures=fee_structures)


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
