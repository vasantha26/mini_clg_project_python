from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('Role', choices=[
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('hod', 'HOD'),
        ('management', 'Management')
    ], validators=[DataRequired()])
    submit = SubmitField('Login')
