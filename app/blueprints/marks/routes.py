from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import bp
from ...models import Exam, Marks, Student, Subject
from ...extensions import db
from ...utils.decorators import staff_required, student_required
from ...services.notification_service import NotificationService
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, DateField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length
from datetime import date


class ExamForm(FlaskForm):
    name = StringField('Exam Name', validators=[DataRequired()])
    exam_type = SelectField('Exam Type', choices=[
        ('assignment', 'Assignment'),
        ('internal', 'Internal'),
        ('final', 'Final')
    ], validators=[DataRequired()])
    subject_id = SelectField('Subject', coerce=int, validators=[DataRequired()])
    max_marks = IntegerField('Maximum Marks', validators=[DataRequired(), NumberRange(min=1)])
    date = DateField('Exam Date', default=date.today)
    year = SelectField('Year', coerce=int, choices=[
        (1, '1st Year'), (2, '2nd Year'), (3, '3rd Year'), (4, '4th Year')
    ], validators=[DataRequired()])
    section = StringField('Section', validators=[DataRequired(), Length(max=10)])
    submit = SubmitField('Create Exam')


@bp.route('/manage')
@login_required
@staff_required
def manage():
    """View and manage exams."""
    staff = current_user.staff
    exams = Exam.query.filter_by(created_by=staff.id).order_by(Exam.date.desc()).all()
    return render_template('marks/manage.html', exams=exams)


@bp.route('/create-exam', methods=['GET', 'POST'])
@login_required
@staff_required
def create_exam():
    """Create a new exam."""
    form = ExamForm()
    staff = current_user.staff

    form.subject_id.choices = [
        (s.id, f'{s.code} - {s.name}') for s in staff.subjects
    ]

    if form.validate_on_submit():
        exam = Exam(
            name=form.name.data,
            exam_type=form.exam_type.data,
            subject_id=form.subject_id.data,
            max_marks=form.max_marks.data,
            date=form.date.data,
            year=form.year.data,
            section=form.section.data,
            department_id=staff.department_id,
            created_by=staff.id
        )
        db.session.add(exam)
        db.session.commit()

        flash('Exam created successfully.', 'success')
        return redirect(url_for('marks.enter', exam_id=exam.id))

    return render_template('marks/create_exam.html', form=form)


@bp.route('/enter/<int:exam_id>', methods=['GET', 'POST'])
@login_required
@staff_required
def enter(exam_id):
    """Enter marks for an exam."""
    exam = Exam.query.get_or_404(exam_id)
    staff = current_user.staff

    if exam.created_by != staff.id:
        flash('You do not have permission to enter marks for this exam.', 'danger')
        return redirect(url_for('marks.manage'))

    students = Student.query.filter_by(
        department_id=exam.department_id,
        year=exam.year,
        section=exam.section
    ).order_by(Student.roll_number).all()

    if request.method == 'POST':
        for student in students:
            marks_value = request.form.get(f'marks_{student.id}')

            if marks_value:
                try:
                    marks_obtained = float(marks_value)
                except ValueError:
                    continue

                # Get or create marks record
                mark = Marks.query.filter_by(
                    exam_id=exam.id,
                    student_id=student.id
                ).first()

                if not mark:
                    mark = Marks(exam_id=exam.id, student_id=student.id)
                    db.session.add(mark)

                mark.marks_obtained = marks_obtained
                mark.calculate_grade(exam.max_marks)

                # Notify student
                NotificationService.notify_result_uploaded(student, exam)

        db.session.commit()
        flash('Marks entered successfully.', 'success')
        return redirect(url_for('marks.manage'))

    # Get existing marks
    existing_marks = {m.student_id: m for m in exam.marks}

    return render_template('marks/enter.html',
                           exam=exam,
                           students=students,
                           existing_marks=existing_marks)


@bp.route('/edit/<int:exam_id>', methods=['GET', 'POST'])
@login_required
@staff_required
def edit_exam(exam_id):
    """Edit an exam."""
    exam = Exam.query.get_or_404(exam_id)
    staff = current_user.staff

    if exam.created_by != staff.id:
        flash('You do not have permission to edit this exam.', 'danger')
        return redirect(url_for('marks.manage'))

    form = ExamForm(obj=exam)
    form.submit.label.text = 'Update Exam'

    # Populate subject choices - all subjects
    all_subjects = Subject.query.all()
    form.subject_id.choices = [
        (s.id, f'{s.code} - {s.name}') for s in all_subjects
    ]

    if form.validate_on_submit():
        exam.name = form.name.data
        exam.exam_type = form.exam_type.data
        exam.subject_id = form.subject_id.data
        exam.max_marks = form.max_marks.data
        exam.date = form.date.data
        exam.year = form.year.data
        exam.section = form.section.data
        db.session.commit()

        flash('Exam updated successfully.', 'success')
        return redirect(url_for('marks.manage'))

    return render_template('marks/edit_exam.html', form=form, exam=exam)


@bp.route('/delete/<int:exam_id>', methods=['POST'])
@login_required
@staff_required
def delete_exam(exam_id):
    """Delete an exam."""
    exam = Exam.query.get_or_404(exam_id)
    staff = current_user.staff

    if exam.created_by != staff.id:
        flash('You do not have permission to delete this exam.', 'danger')
        return redirect(url_for('marks.manage'))

    # Delete associated marks first
    Marks.query.filter_by(exam_id=exam.id).delete()
    db.session.delete(exam)
    db.session.commit()

    flash('Exam deleted successfully.', 'success')
    return redirect(url_for('marks.manage'))


@bp.route('/reports')
@login_required
@staff_required
def reports():
    """View marks reports."""
    staff = current_user.staff
    exams = Exam.query.filter_by(created_by=staff.id).order_by(Exam.date.desc()).all()
    return render_template('marks/reports.html', exams=exams)


@bp.route('/my-results')
@login_required
@student_required
def my_results():
    """View own results."""
    student = current_user.student

    marks = Marks.query.filter_by(student_id=student.id).order_by(
        Marks.entered_at.desc()
    ).all()

    # Group by subject
    results_by_subject = {}
    for mark in marks:
        subject_name = mark.exam.subject.name
        if subject_name not in results_by_subject:
            results_by_subject[subject_name] = []
        results_by_subject[subject_name].append(mark)

    return render_template('marks/my_results.html',
                           student=student,
                           results_by_subject=results_by_subject)
