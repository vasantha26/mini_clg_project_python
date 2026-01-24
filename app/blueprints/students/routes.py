from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import bp
from ...models import User, Student, Department
from ...extensions import db
from ...utils.decorators import staff_required
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, DateField, TextAreaField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from datetime import date


class StudentRegistrationForm(FlaskForm):
    # User info
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])

    # Student info
    roll_number = StringField('Roll Number', validators=[DataRequired(), Length(max=20)])
    name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    year = SelectField('Year', coerce=int, choices=[
        (1, '1st Year'), (2, '2nd Year'), (3, '3rd Year'), (4, '4th Year')
    ], validators=[DataRequired()])
    semester = SelectField('Semester', coerce=int, choices=[
        (1, '1'), (2, '2'), (3, '3'), (4, '4'),
        (5, '5'), (6, '6'), (7, '7'), (8, '8')
    ], validators=[DataRequired()])
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    section = SelectField('Section', choices=[
        ('A', 'Section A'), ('B', 'Section B'), ('C', 'Section C')
    ], validators=[DataRequired()])
    phone = StringField('Phone')
    address = TextAreaField('Address')
    admission_date = DateField('Admission Date', default=date.today)

    submit = SubmitField('Register Student')


@bp.route('/list')
@login_required
@staff_required
def list():
    """List all students."""
    staff = current_user.staff

    # Filter by department if staff
    department_id = request.args.get('department_id', type=int)
    year = request.args.get('year', type=int)
    section = request.args.get('section')

    query = Student.query

    if department_id:
        query = query.filter_by(department_id=department_id)
    else:
        query = query.filter_by(department_id=staff.department_id)

    if year:
        query = query.filter_by(year=year)
    if section:
        query = query.filter_by(section=section)

    students = query.order_by(Student.roll_number).all()
    departments = Department.query.all()

    return render_template('students/list.html',
                           students=students,
                           departments=departments)


@bp.route('/register', methods=['GET', 'POST'])
@login_required
@staff_required
def register():
    """Register a new student."""
    form = StudentRegistrationForm()

    departments = Department.query.all()
    form.department_id.choices = [(d.id, d.name) for d in departments]

    if form.validate_on_submit():
        # Check if username or email already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists.', 'danger')
            return render_template('students/register.html', form=form)

        if User.query.filter_by(email=form.email.data).first():
            flash('Email already exists.', 'danger')
            return render_template('students/register.html', form=form)

        if Student.query.filter_by(roll_number=form.roll_number.data).first():
            flash('Roll number already exists.', 'danger')
            return render_template('students/register.html', form=form)

        # Create user
        user = User(
            username=form.username.data,
            email=form.email.data,
            role='student'
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()  # Get user ID

        # Create student
        student = Student(
            user_id=user.id,
            roll_number=form.roll_number.data,
            name=form.name.data,
            year=form.year.data,
            semester=form.semester.data,
            department_id=form.department_id.data,
            section=form.section.data,
            phone=form.phone.data,
            address=form.address.data,
            admission_date=form.admission_date.data
        )
        db.session.add(student)
        db.session.commit()

        flash(f'Student {student.name} registered successfully.', 'success')
        return redirect(url_for('students.list'))

    return render_template('students/register.html', form=form)


@bp.route('/detail/<int:id>')
@login_required
@staff_required
def detail(id):
    """View student details."""
    student = Student.query.get_or_404(id)

    # Get attendance summary
    from ...models import AttendanceSummary
    attendance = AttendanceSummary.query.filter_by(student_id=student.id).all()

    # Get marks
    from ...models import Marks
    marks = Marks.query.filter_by(student_id=student.id).all()

    # Get fees
    from ...models import StudentFees
    fees = StudentFees.query.filter_by(student_id=student.id).all()

    return render_template('students/detail.html',
                           student=student,
                           attendance=attendance,
                           marks=marks,
                           fees=fees)
