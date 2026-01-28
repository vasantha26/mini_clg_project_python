from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, DateField, SubmitField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Optional
from datetime import date


class HODRegistrationForm(FlaskForm):
    # User info
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])

    # Staff/HOD info
    employee_id = StringField('Employee ID', validators=[DataRequired(), Length(max=20)])
    name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    designation = StringField('Designation', validators=[DataRequired(), Length(max=50)], default='Head of Department')
    phone = StringField('Phone', validators=[Optional(), Length(max=15)])
    qualification = StringField('Qualification', validators=[Optional(), Length(max=100)])
    joining_date = DateField('Joining Date', default=date.today)

    submit = SubmitField('Create HOD')


class HODEditForm(FlaskForm):
    # User info
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('New Password (leave blank to keep current)', validators=[Optional(), Length(min=6)])

    # Staff/HOD info
    employee_id = StringField('Employee ID', validators=[DataRequired(), Length(max=20)])
    name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    designation = StringField('Designation', validators=[DataRequired(), Length(max=50)])
    phone = StringField('Phone', validators=[Optional(), Length(max=15)])
    qualification = StringField('Qualification', validators=[Optional(), Length(max=100)])
    joining_date = DateField('Joining Date')

    submit = SubmitField('Update HOD')


class StaffRegistrationForm(FlaskForm):
    # User info
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])

    # Staff info
    employee_id = StringField('Employee ID', validators=[DataRequired(), Length(max=20)])
    name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    designation = StringField('Designation', validators=[DataRequired(), Length(max=50)], default='Assistant Professor')
    phone = StringField('Phone', validators=[Optional(), Length(max=15)])
    qualification = StringField('Qualification', validators=[Optional(), Length(max=100)])
    joining_date = DateField('Joining Date', default=date.today)

    submit = SubmitField('Create Staff')


class StaffEditForm(FlaskForm):
    # User info
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('New Password (leave blank to keep current)', validators=[Optional(), Length(min=6)])

    # Staff info
    employee_id = StringField('Employee ID', validators=[DataRequired(), Length(max=20)])
    name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    designation = StringField('Designation', validators=[DataRequired(), Length(max=50)])
    phone = StringField('Phone', validators=[Optional(), Length(max=15)])
    qualification = StringField('Qualification', validators=[Optional(), Length(max=100)])
    joining_date = DateField('Joining Date')

    submit = SubmitField('Update Staff')


class SubjectForm(FlaskForm):
    code = StringField('Subject Code', validators=[DataRequired(), Length(max=20)])
    name = StringField('Subject Name', validators=[DataRequired(), Length(max=100)])
    year = SelectField('Year', coerce=int, choices=[
        (1, '1st Year'), (2, '2nd Year'), (3, '3rd Year'), (4, '4th Year')
    ], validators=[DataRequired()])
    semester = SelectField('Semester', coerce=int, choices=[
        (1, '1'), (2, '2'), (3, '3'), (4, '4'),
        (5, '5'), (6, '6'), (7, '7'), (8, '8')
    ], validators=[DataRequired()])
    credits = IntegerField('Credits', validators=[DataRequired()], default=3)
    is_lab = BooleanField('Is Lab Subject')

    submit = SubmitField('Save Subject')


class DepartmentForm(FlaskForm):
    code = StringField('Department Code', validators=[DataRequired(), Length(max=10)])
    name = StringField('Department Name', validators=[DataRequired(), Length(max=100)])

    submit = SubmitField('Save Department')
