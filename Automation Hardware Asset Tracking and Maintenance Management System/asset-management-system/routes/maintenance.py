import os
from datetime import date, datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from models import db
from models.maintenance import Maintenance
from models.asset import Asset
from utils.helpers import log_activity
from utils.decorators import admin_required

maintenance_bp = Blueprint('maintenance', __name__)


@maintenance_bp.route('/maintenance')
@login_required
def list_maintenance():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    status_filter = request.args.get('status', '')

    query = Maintenance.query

    if status_filter:
        query = query.filter(Maintenance.status == status_filter)

    query = query.order_by(Maintenance.maintenance_date.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    records = pagination.items

    return render_template(
        'maintenance/list.html',
        records=records,
        pagination=pagination,
        status_filter=status_filter
    )


@maintenance_bp.route('/assets/<int:asset_id>/maintenance/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_maintenance(asset_id):
    asset = Asset.query.get_or_404(asset_id)

    if request.method == 'POST':
        maint_date = None
        if request.form.get('maintenance_date'):
            try:
                maint_date = date.fromisoformat(request.form['maintenance_date'])
            except ValueError:
                pass

        attachment_path = None
        if 'attachment' in request.files:
            file = request.files['attachment']
            if file and file.filename:
                ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                if ext in current_app.config['ALLOWED_EXTENSIONS']:
                    filename = secure_filename(f"maint_{asset_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.{ext}")
                    os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    attachment_path = filename

        record = Maintenance(
            asset_id=asset_id,
            maintenance_date=maint_date or date.today(),
            engineer=request.form.get('engineer', current_user.full_name),
            description=request.form.get('description', ''),
            status=request.form.get('status', 'Scheduled'),
            attachment=attachment_path
        )
        db.session.add(record)
        db.session.commit()

        log_activity(
            current_user.id, current_user.username,
            'Add Maintenance',
            f'Added maintenance record for asset {asset.asset_tag}'
        )
        flash('Maintenance record created successfully.', 'success')
        return redirect(url_for('assets.detail_asset', asset_id=asset_id))

    return render_template('maintenance/form.html', asset=asset, record=None)


@maintenance_bp.route('/maintenance/<int:maint_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_maintenance(maint_id):
    record = Maintenance.query.get_or_404(maint_id)
    asset = Asset.query.get(record.asset_id)

    if request.method == 'POST':
        maint_date = None
        if request.form.get('maintenance_date'):
            try:
                maint_date = date.fromisoformat(request.form['maintenance_date'])
            except ValueError:
                maint_date = record.maintenance_date

        record.maintenance_date = maint_date or record.maintenance_date
        record.engineer = request.form.get('engineer', record.engineer)
        record.description = request.form.get('description', record.description)
        record.status = request.form.get('status', record.status)
        db.session.commit()

        log_activity(
            current_user.id, current_user.username,
            'Edit Maintenance',
            f'Edited maintenance record #{maint_id} for asset {asset.asset_tag if asset else "Unknown"}'
        )
        flash('Maintenance record updated successfully.', 'success')
        return redirect(url_for('assets.detail_asset', asset_id=record.asset_id))

    return render_template('maintenance/form.html', asset=asset, record=record)


@maintenance_bp.route('/maintenance/<int:maint_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_maintenance(maint_id):
    record = Maintenance.query.get_or_404(maint_id)
    asset_id = record.asset_id

    if record.attachment:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], record.attachment)
        if os.path.exists(filepath):
            os.remove(filepath)

    db.session.delete(record)
    db.session.commit()

    log_activity(
        current_user.id, current_user.username,
        'Delete Maintenance',
        f'Deleted maintenance record #{maint_id}'
    )
    flash('Maintenance record deleted.', 'success')
    return redirect(url_for('assets.detail_asset', asset_id=asset_id))
