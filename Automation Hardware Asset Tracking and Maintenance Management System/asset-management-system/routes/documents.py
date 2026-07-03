import os
import json
from flask import Blueprint, redirect, url_for, flash, current_app, send_file
from flask_login import login_required, current_user
from models import db
from models.document import Document
from models.asset import Asset
from utils.decorators import admin_required
from utils.helpers import log_activity

documents_bp = Blueprint('documents', __name__)


@documents_bp.route('/documents/<int:doc_id>/download')
@login_required
def download_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], doc.filename)

    if not os.path.exists(file_path):
        flash('File not found on server.', 'danger')
        return redirect(url_for('assets.detail_asset', asset_id=doc.asset_id))

    return send_file(file_path, as_attachment=True, download_name=doc.original_filename)


@documents_bp.route('/documents/<int:doc_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    asset_id = doc.asset_id
    asset = Asset.query.get(asset_id)

    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], doc.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    log_activity(
        current_user.id, current_user.username,
        'Delete File', f'Deleted {doc.original_filename} from asset {asset.asset_tag if asset else "Unknown"}'
    )

    db.session.delete(doc)
    db.session.commit()
    flash('Document deleted successfully.', 'success')
    return redirect(url_for('assets.detail_asset', asset_id=asset_id))
