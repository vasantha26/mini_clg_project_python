from flask import Flask
from .config import Config
from .extensions import db, login_manager, csrf


def create_app(config_class=Config):
    app = Flask(__name__, static_folder='../static')
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from .blueprints.auth import bp as auth_bp
    from .blueprints.dashboard import bp as dashboard_bp
    from .blueprints.attendance import bp as attendance_bp
    from .blueprints.marks import bp as marks_bp
    from .blueprints.fees import bp as fees_bp
    from .blueprints.library import bp as library_bp
    from .blueprints.complaints import bp as complaints_bp
    from .blueprints.feedback import bp as feedback_bp
    from .blueprints.notices import bp as notices_bp
    from .blueprints.timetable import bp as timetable_bp
    from .blueprints.students import bp as students_bp
    from .blueprints.notifications import bp as notifications_bp
    from .blueprints.usermanagement import bp as usermanagement_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(attendance_bp, url_prefix='/attendance')
    app.register_blueprint(marks_bp, url_prefix='/marks')
    app.register_blueprint(fees_bp, url_prefix='/fees')
    app.register_blueprint(library_bp, url_prefix='/library')
    app.register_blueprint(complaints_bp, url_prefix='/complaints')
    app.register_blueprint(feedback_bp, url_prefix='/feedback')
    app.register_blueprint(notices_bp, url_prefix='/notices')
    app.register_blueprint(timetable_bp, url_prefix='/timetable')
    app.register_blueprint(students_bp, url_prefix='/students')
    app.register_blueprint(notifications_bp, url_prefix='/notifications')
    app.register_blueprint(usermanagement_bp, url_prefix='/manage')

    # Create database tables
    with app.app_context():
        db.create_all()

    return app
