from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length
from datetime import date


class AttendanceSessionForm(FlaskForm):
    subject_id = SelectField('Subject', coerce=int, validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()], default=date.today)
    period = IntegerField('Period', validators=[DataRequired(), NumberRange(min=1, max=8)])
    year = SelectField('Year', coerce=int, choices=[
        (1, '1st Year'), (2, '2nd Year'), (3, '3rd Year'), (4, '4th Year')
    ], validators=[DataRequired()])
    section = StringField('Section', validators=[DataRequired(), Length(max=10)])
    submit = SubmitField('Create Session')
