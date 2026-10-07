from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from services.login_throttle import (
    clear_account_failures,
    record_failure,
    retry_after,
)
from utils.helpers import log_activity

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()[:80]
        password = request.form.get('password', '')[:1024]
        remember = request.form.get('remember')
        client_ip = request.remote_addr or 'unknown'

        wait_seconds = retry_after(client_ip, username)
        if wait_seconds:
            current_app.logger.warning(
                'Blocked throttled login attempt from %s', client_ip
            )
            flash('Too many login attempts. Please try again later.', 'danger')
            response = render_template('login.html'), 429
            response = current_app.make_response(response)
            response.headers['Retry-After'] = str(wait_seconds)
            return response

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            clear_account_failures(client_ip, username)
            login_user(user, remember=bool(remember))
            log_activity(user.id, user.username, 'Login', f'User {user.username} logged in')
            flash(f'Welcome back, {user.full_name}!', 'success')
            return redirect(url_for('dashboard.index'))

        wait_seconds = record_failure(client_ip, username)
        current_app.logger.warning('Failed login attempt from %s', client_ip)
        flash('Invalid username or password.', 'danger')
        if wait_seconds:
            response = current_app.make_response((render_template('login.html'), 429))
            response.headers['Retry-After'] = str(wait_seconds)
            return response

    return render_template('login.html')


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    log_activity(current_user.id, current_user.username, 'Logout', f'User {current_user.username} logged out')
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
