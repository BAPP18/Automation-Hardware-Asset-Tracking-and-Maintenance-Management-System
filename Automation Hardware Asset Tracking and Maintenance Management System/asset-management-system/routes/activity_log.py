from flask import Blueprint, render_template, request
from flask_login import login_required
from models.activity_log import ActivityLog

activity_bp = Blueprint('activity', __name__)


@activity_bp.route('/activity-log')
@login_required
def list_activity():
    page = request.args.get('page', 1, type=int)
    per_page = 30
    action_filter = request.args.get('action', '')

    query = ActivityLog.query

    if action_filter:
        query = query.filter(ActivityLog.action == action_filter)

    query = query.order_by(ActivityLog.timestamp.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    logs = pagination.items

    actions = [
        'Login', 'Logout', 'Add Asset', 'Edit Asset', 'Delete Asset',
        'Upload File', 'Delete File', 'Import Excel', 'Export Excel',
        'Add Maintenance', 'Edit Maintenance', 'Delete Maintenance'
    ]

    return render_template(
        'activity_log.html',
        logs=logs,
        pagination=pagination,
        action_filter=action_filter,
        actions=actions
    )
