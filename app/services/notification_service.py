from ..extensions import db
from ..models import Notification, User, Staff, Management


class NotificationService:
    @staticmethod
    def create_notification(user_id, notification_type, title, message,
                            reference_type=None, reference_id=None):
        """Create a notification for a specific user."""
        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            reference_type=reference_type,
            reference_id=reference_id
        )
        db.session.add(notification)
        db.session.commit()
        return notification

    @staticmethod
    def notify_low_attendance(student, subject, percentage):
        """Notify student and staff about low attendance."""
        # Notify student
        NotificationService.create_notification(
            user_id=student.user_id,
            notification_type='low_attendance',
            title='Low Attendance Warning',
            message=f'Your attendance in {subject.name} is {percentage:.1f}%, which is below the required 75%.',
            reference_type='attendance',
            reference_id=subject.id
        )

        # Notify staff members teaching this subject
        for staff in subject.staff_members:
            NotificationService.create_notification(
                user_id=staff.user_id,
                notification_type='low_attendance',
                title='Student Low Attendance Alert',
                message=f'{student.name} (Roll: {student.roll_number}) has {percentage:.1f}% attendance in {subject.name}.',
                reference_type='attendance',
                reference_id=subject.id
            )

    @staticmethod
    def notify_utility_complaint(complaint):
        """Notify management about utility complaint."""
        management_users = User.query.filter_by(role='management').all()
        for user in management_users:
            NotificationService.create_notification(
                user_id=user.id,
                notification_type='utility_complaint',
                title='New Utility Complaint',
                message=f'New utility complaint: {complaint.subject}',
                reference_type='complaint',
                reference_id=complaint.id
            )

    @staticmethod
    def notify_academic_complaint(complaint):
        """Notify staff and management about academic complaint."""
        # Notify assigned staff if any
        if complaint.assigned_to:
            staff = Staff.query.get(complaint.assigned_to)
            if staff:
                NotificationService.create_notification(
                    user_id=staff.user_id,
                    notification_type='academic_complaint',
                    title='Academic Complaint Assigned',
                    message=f'You have been assigned a complaint: {complaint.subject}',
                    reference_type='complaint',
                    reference_id=complaint.id
                )

        # Notify management
        management_users = User.query.filter_by(role='management').all()
        for user in management_users:
            NotificationService.create_notification(
                user_id=user.id,
                notification_type='academic_complaint',
                title='New Academic Complaint',
                message=f'New academic complaint: {complaint.subject}',
                reference_type='complaint',
                reference_id=complaint.id
            )

    @staticmethod
    def notify_staff_feedback(feedback):
        """Notify target staff and management about staff feedback."""
        if feedback.target_staff_id:
            staff = Staff.query.get(feedback.target_staff_id)
            if staff:
                NotificationService.create_notification(
                    user_id=staff.user_id,
                    notification_type='staff_feedback',
                    title='New Feedback Received',
                    message=f'You have received new feedback (Rating: {feedback.rating}/5).',
                    reference_type='feedback',
                    reference_id=feedback.id
                )

        # Notify management
        management_users = User.query.filter_by(role='management').all()
        for user in management_users:
            NotificationService.create_notification(
                user_id=user.id,
                notification_type='staff_feedback',
                title='New Staff Feedback',
                message=f'New staff feedback received (Rating: {feedback.rating}/5).',
                reference_type='feedback',
                reference_id=feedback.id
            )

    @staticmethod
    def notify_general_feedback(feedback):
        """Notify all staff and management about general feedback."""
        staff_users = User.query.filter(User.role.in_(['staff', 'hod'])).all()
        for user in staff_users:
            NotificationService.create_notification(
                user_id=user.id,
                notification_type='general_feedback',
                title='New General Feedback',
                message=f'New general feedback received (Rating: {feedback.rating}/5).',
                reference_type='feedback',
                reference_id=feedback.id
            )

        management_users = User.query.filter_by(role='management').all()
        for user in management_users:
            NotificationService.create_notification(
                user_id=user.id,
                notification_type='general_feedback',
                title='New General Feedback',
                message=f'New general feedback received (Rating: {feedback.rating}/5).',
                reference_type='feedback',
                reference_id=feedback.id
            )

    @staticmethod
    def notify_new_notice(notice):
        """Notify all relevant users about new notice."""
        users = User.query.filter_by(is_active=True).all()
        for user in users:
            NotificationService.create_notification(
                user_id=user.id,
                notification_type='new_notice',
                title='New Notice Posted',
                message=f'{notice.title}',
                reference_type='notice',
                reference_id=notice.id
            )

    @staticmethod
    def notify_result_uploaded(student, exam):
        """Notify student about result upload."""
        NotificationService.create_notification(
            user_id=student.user_id,
            notification_type='result_uploaded',
            title='Result Uploaded',
            message=f'Your result for {exam.name} in {exam.subject.name} has been uploaded.',
            reference_type='marks',
            reference_id=exam.id
        )

    @staticmethod
    def get_unread_count(user_id):
        """Get count of unread notifications for a user."""
        return Notification.query.filter_by(user_id=user_id, is_read=False).count()

    @staticmethod
    def mark_as_read(notification_id, user_id):
        """Mark a notification as read."""
        notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        if notification:
            notification.is_read = True
            db.session.commit()
            return True
        return False

    @staticmethod
    def mark_all_as_read(user_id):
        """Mark all notifications as read for a user."""
        Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
        db.session.commit()
