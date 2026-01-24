from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import bp
from ...models import Book, BookIssue, Student
from ...extensions import db
from ...utils.decorators import management_required, student_required
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class BookForm(FlaskForm):
    isbn = StringField('ISBN', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    publisher = StringField('Publisher')
    publication_year = IntegerField('Publication Year')
    category = StringField('Category')
    total_copies = IntegerField('Total Copies', validators=[DataRequired(), NumberRange(min=1)], default=1)
    location = StringField('Location (Shelf/Rack)')
    submit = SubmitField('Add Book')


@bp.route('/search')
@login_required
def search():
    """Search for books."""
    query = request.args.get('q', '')
    books = []

    if query:
        books = Book.query.filter(
            db.or_(
                Book.title.ilike(f'%{query}%'),
                Book.author.ilike(f'%{query}%'),
                Book.isbn.ilike(f'%{query}%')
            )
        ).all()

    return render_template('library/search.html', books=books, query=query)


@bp.route('/availability')
@login_required
def availability():
    """View available books."""
    books = Book.query.filter(Book.available_copies > 0).order_by(Book.title).all()
    return render_template('library/availability.html', books=books)


@bp.route('/my-books')
@login_required
@student_required
def my_books():
    """View borrowed books."""
    student = current_user.student
    issues = BookIssue.query.filter_by(student_id=student.id).order_by(
        BookIssue.issue_date.desc()
    ).all()

    # Update overdue status
    for issue in issues:
        if issue.is_overdue() and issue.status == 'issued':
            issue.status = 'overdue'
            issue.calculate_fine()

    db.session.commit()

    return render_template('library/my_books.html', student=student, issues=issues)


@bp.route('/manage', methods=['GET', 'POST'])
@login_required
@management_required
def manage():
    """Manage library books."""
    form = BookForm()

    if form.validate_on_submit():
        # Check if ISBN already exists
        existing = Book.query.filter_by(isbn=form.isbn.data).first()
        if existing:
            flash('A book with this ISBN already exists.', 'warning')
        else:
            book = Book(
                isbn=form.isbn.data,
                title=form.title.data,
                author=form.author.data,
                publisher=form.publisher.data,
                publication_year=form.publication_year.data,
                category=form.category.data,
                total_copies=form.total_copies.data,
                available_copies=form.total_copies.data,
                location=form.location.data
            )
            db.session.add(book)
            db.session.commit()
            flash('Book added successfully.', 'success')
            return redirect(url_for('library.manage'))

    books = Book.query.order_by(Book.added_at.desc()).all()
    return render_template('library/manage.html', form=form, books=books)


@bp.route('/issue/<int:book_id>', methods=['GET', 'POST'])
@login_required
@management_required
def issue(book_id):
    """Issue a book to a student."""
    book = Book.query.get_or_404(book_id)

    if not book.is_available():
        flash('This book is not available for issue.', 'danger')
        return redirect(url_for('library.manage'))

    if request.method == 'POST':
        roll_number = request.form.get('roll_number')
        student = Student.query.filter_by(roll_number=roll_number).first()

        if not student:
            flash('Student not found.', 'danger')
        else:
            # Check if student already has this book
            existing = BookIssue.query.filter_by(
                book_id=book.id,
                student_id=student.id,
                status='issued'
            ).first()

            if existing:
                flash('Student already has this book issued.', 'warning')
            else:
                issue = BookIssue(book_id=book.id, student_id=student.id)
                book.available_copies -= 1
                db.session.add(issue)
                db.session.commit()
                flash(f'Book issued to {student.name}.', 'success')
                return redirect(url_for('library.manage'))

    return render_template('library/issue.html', book=book)


@bp.route('/return/<int:issue_id>', methods=['POST'])
@login_required
@management_required
def return_book(issue_id):
    """Return a book."""
    from datetime import datetime
    issue = BookIssue.query.get_or_404(issue_id)

    if issue.status == 'returned':
        flash('This book has already been returned.', 'warning')
    else:
        issue.status = 'returned'
        issue.return_date = datetime.utcnow()
        issue.book.available_copies += 1
        db.session.commit()
        flash('Book returned successfully.', 'success')

    return redirect(url_for('library.manage'))
