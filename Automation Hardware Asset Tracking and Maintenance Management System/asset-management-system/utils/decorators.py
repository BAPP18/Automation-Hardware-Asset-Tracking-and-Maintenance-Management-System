from functools import wraps
from flask import abort, redirect, url_for, flash
from flask_login import current_user


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def engineer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if current_user.role not in ('Admin', 'Engineer'):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
