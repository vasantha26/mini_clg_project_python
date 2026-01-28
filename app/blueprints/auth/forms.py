from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, DateField
from wtforms.validators import DataRequired, Length


class StudentLoginForm(FlaskForm):
    """Student login with Roll Number and Date of Birth."""
    roll_number = StringField('Roll Number', validators=[DataRequired(), Length(max=20)])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    submit = SubmitField('Login as Student')


class StaffLoginForm(FlaskForm):
    """Staff/HOD/Management login with Username and Password."""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('Role', choices=[
        ('staff', 'Staff'),
        ('hod', 'HOD'),
        ('management', 'Management')
    ], validators=[DataRequired()])
    submit = SubmitField('Login')
