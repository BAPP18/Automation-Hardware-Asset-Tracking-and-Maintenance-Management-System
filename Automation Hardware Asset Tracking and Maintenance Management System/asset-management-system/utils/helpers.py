import os
from datetime import date
from flask import current_app
from models.activity_log import ActivityLog
from models import db


def log_activity(user_id, username, action, description=None):
    log = ActivityLog(
        user_id=user_id,
        username=username,
        action=action,
        description=description
    )
    db.session.add(log)
    db.session.commit()


def allowed_file(filename):
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config['ALLOWED_EXTENSIONS']


def format_file_size(size_bytes):
    if not size_bytes:
        return '0 B'
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f'{size_bytes:.1f} {unit}'
        size_bytes /= 1024
    return f'{size_bytes:.1f} TB'


def get_warranty_badge_class(days_left):
    if days_left is None:
        return 'secondary'
    if days_left < 0:
        return 'danger'
    elif days_left <= 30:
        return 'danger'
    elif days_left <= 90:
        return 'warning'
    return 'success'
