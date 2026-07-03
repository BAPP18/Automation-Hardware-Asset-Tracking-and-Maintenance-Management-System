import json
import os
from datetime import date, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from models import db
from models.asset import Asset
from models.vendor import Vendor
from models.department import Department
from models.document import Document
from models.maintenance import Maintenance
from services.import_service import import_assets_from_excel
from services.export_service import export_assets_excel, export_maintenance_excel
from services.file_service import save_uploaded_file
from utils.helpers import log_activity, allowed_file, format_file_size, get_warranty_badge_class
from utils.decorators import admin_required

assets_bp = Blueprint('assets', __name__)


@assets_bp.route('/assets')
@login_required
def list_assets():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    category_filter = request.args.get('category', '')
    department_filter = request.args.get('department', '')

    query = Asset.query

    if search:
        query = query.filter(
            db.or_(
                Asset.asset_tag.ilike(f'%{search}%'),
                Asset.device_name.ilike(f'%{search}%'),
                Asset.serial_number.ilike(f'%{search}%'),
                Asset.assigned_user.ilike(f'%{search}%'),
                Asset.location.ilike(f'%{search}%')
            )
        )

    if status_filter:
        query = query.filter(Asset.status == status_filter)
    if category_filter:
        query = query.filter(Asset.category == category_filter)
    if department_filter:
        query = query.filter(Asset.department_id == int(department_filter))

    query = query.order_by(Asset.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    assets = pagination.items

    categories = db.session.query(Asset.category.distinct()).all()
    categories = [c[0] for c in categories if c[0]]
    departments = Department.query.all()
    statuses = ['Available', 'Assigned', 'Maintenance', 'Retired']

    return render_template(
        'assets/list.html',
        assets=assets,
        pagination=pagination,
        search=search,
        status_filter=status_filter,
        category_filter=category_filter,
        department_filter=department_filter,
        categories=categories,
        departments=departments,
        statuses=statuses
    )


@assets_bp.route('/assets/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_asset():
    vendors = Vendor.query.order_by(Vendor.name).all()
    departments = Department.query.order_by(Department.name).all()

    if request.method == 'POST':
        asset_tag = request.form.get('asset_tag', '').strip()
        if not asset_tag:
            flash('Asset Tag is required.', 'danger')
            return render_template('assets/form.html', vendors=vendors, departments=departments, asset=None)

        existing = Asset.query.filter_by(asset_tag=asset_tag).first()
        if existing:
            flash(f'Asset Tag "{asset_tag}" already exists.', 'danger')
            return render_template('assets/form.html', vendors=vendors, departments=departments, asset=None)

        purchase_date = None
        if request.form.get('purchase_date'):
            try:
                purchase_date = date.fromisoformat(request.form['purchase_date'])
            except ValueError:
                pass

        warranty_exp = None
        if request.form.get('warranty_expiration'):
            try:
                warranty_exp = date.fromisoformat(request.form['warranty_expiration'])
            except ValueError:
                pass

        asset = Asset(
            asset_tag=asset_tag,
            device_name=request.form.get('device_name', ''),
            category=request.form.get('category', ''),
            brand=request.form.get('brand', ''),
            model=request.form.get('model', ''),
            serial_number=request.form.get('serial_number', ''),
            purchase_date=purchase_date,
            warranty_expiration=warranty_exp,
            vendor_id=request.form.get('vendor_id', type=int) or None,
            assigned_user=request.form.get('assigned_user', ''),
            department_id=request.form.get('department_id', type=int) or None,
            location=request.form.get('location', ''),
            status=request.form.get('status', 'Available'),
            condition=request.form.get('condition', 'Good'),
            notes=request.form.get('notes', '')
        )
        db.session.add(asset)
        db.session.commit()

        log_activity(
            current_user.id, current_user.username,
            'Add Asset', f'Added asset {asset.asset_tag} - {asset.device_name}'
        )
        flash('Asset created successfully.', 'success')
        return redirect(url_for('assets.detail_asset', asset_id=asset.id))

    return render_template('assets/form.html', vendors=vendors, departments=departments, asset=None)


@assets_bp.route('/assets/<int:asset_id>')
@login_required
def detail_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    documents = Document.query.filter_by(asset_id=asset_id).order_by(Document.uploaded_at.desc()).all()
    maintenance_records = Maintenance.query.filter_by(asset_id=asset_id).order_by(Maintenance.maintenance_date.desc()).all()

    doc_info_list = []
    for doc in documents:
        info = {}
        if doc.file_info:
            try:
                info = json.loads(doc.file_info)
            except (json.JSONDecodeError, TypeError):
                info = {}
        doc_info_list.append({'doc': doc, 'info': info})

    return render_template(
        'assets/detail.html',
        asset=asset,
        doc_info_list=doc_info_list,
        maintenance_records=maintenance_records,
        format_file_size=format_file_size,
        get_warranty_badge_class=get_warranty_badge_class
    )


@assets_bp.route('/assets/<int:asset_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    vendors = Vendor.query.order_by(Vendor.name).all()
    departments = Department.query.order_by(Department.name).all()

    if request.method == 'POST':
        asset_tag = request.form.get('asset_tag', '').strip()
        if not asset_tag:
            flash('Asset Tag is required.', 'danger')
            return render_template('assets/form.html', vendors=vendors, departments=departments, asset=asset)

        existing = Asset.query.filter(Asset.asset_tag == asset_tag, Asset.id != asset_id).first()
        if existing:
            flash(f'Asset Tag "{asset_tag}" already exists.', 'danger')
            return render_template('assets/form.html', vendors=vendors, departments=departments, asset=asset)

        purchase_date = None
        if request.form.get('purchase_date'):
            try:
                purchase_date = date.fromisoformat(request.form['purchase_date'])
            except ValueError:
                purchase_date = asset.purchase_date

        warranty_exp = None
        if request.form.get('warranty_expiration'):
            try:
                warranty_exp = date.fromisoformat(request.form['warranty_expiration'])
            except ValueError:
                warranty_exp = asset.warranty_expiration

        asset.asset_tag = asset_tag
        asset.device_name = request.form.get('device_name', '')
        asset.category = request.form.get('category', '')
        asset.brand = request.form.get('brand', '')
        asset.model = request.form.get('model', '')
        asset.serial_number = request.form.get('serial_number', '')
        asset.purchase_date = purchase_date
        asset.warranty_expiration = warranty_exp
        asset.vendor_id = request.form.get('vendor_id', type=int) or None
        asset.assigned_user = request.form.get('assigned_user', '')
        asset.department_id = request.form.get('department_id', type=int) or None
        asset.location = request.form.get('location', '')
        asset.status = request.form.get('status', 'Available')
        asset.condition = request.form.get('condition', 'Good')
        asset.notes = request.form.get('notes', '')
        db.session.commit()

        log_activity(
            current_user.id, current_user.username,
            'Edit Asset', f'Edited asset {asset.asset_tag} - {asset.device_name}'
        )
        flash('Asset updated successfully.', 'success')
        return redirect(url_for('assets.detail_asset', asset_id=asset.id))

    return render_template('assets/form.html', vendors=vendors, departments=departments, asset=asset)


@assets_bp.route('/assets/<int:asset_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    tag = asset.asset_tag
    name = asset.device_name

    for doc in asset.documents:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], doc.filename)
        if os.path.exists(file_path):
            os.remove(file_path)

    db.session.delete(asset)
    db.session.commit()

    log_activity(
        current_user.id, current_user.username,
        'Delete Asset', f'Deleted asset {tag} - {name}'
    )
    flash('Asset deleted successfully.', 'success')
    return redirect(url_for('assets.list_assets'))


@assets_bp.route('/import', methods=['GET', 'POST'])
@login_required
@admin_required
def import_assets():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected.', 'danger')
            return render_template('import.html')

        file = request.files['file']
        if file.filename == '':
            flash('No file selected.', 'danger')
            return render_template('import.html')

        if not file.filename.endswith('.xlsx'):
            flash('Please upload an .xlsx file.', 'danger')
            return render_template('import.html')

        filename = secure_filename(file.filename)
        temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f'_import_{filename}')
        file.save(temp_path)

        imported, errors = import_assets_from_excel(temp_path)

        if os.path.exists(temp_path):
            os.remove(temp_path)

        log_activity(
            current_user.id, current_user.username,
            'Import Excel', f'Imported {imported} assets from {filename}'
        )

        if imported > 0:
            flash(f'Successfully imported {imported} assets.', 'success')
        if errors:
            for err in errors[:10]:
                flash(err, 'warning')

        return redirect(url_for('assets.list_assets'))

    return render_template('import.html')


@assets_bp.route('/export/assets')
@login_required
def export_assets():
    try:
        filepath, filename = export_assets_excel()
        log_activity(
            current_user.id, current_user.username,
            'Export Excel', f'Exported asset list to {filename}'
        )
        return send_file(filepath, as_attachment=True, download_name=filename)
    except Exception as e:
        flash(f'Error exporting assets: {str(e)}', 'danger')
        return redirect(url_for('assets.list_assets'))


@assets_bp.route('/export/maintenance')
@login_required
def export_maintenance():
    try:
        filepath, filename = export_maintenance_excel()
        log_activity(
            current_user.id, current_user.username,
            'Export Excel', f'Exported maintenance report to {filename}'
        )
        return send_file(filepath, as_attachment=True, download_name=filename)
    except Exception as e:
        flash(f'Error exporting maintenance report: {str(e)}', 'danger')
        return redirect(url_for('maintenance.list_maintenance'))


@assets_bp.route('/assets/<int:asset_id>/upload', methods=['POST'])
@login_required
@admin_required
def upload_document(asset_id):
    asset = Asset.query.get_or_404(asset_id)

    if 'file' not in request.files:
        flash('No file selected.', 'danger')
        return redirect(url_for('assets.detail_asset', asset_id=asset_id))

    file = request.files['file']
    if file.filename == '':
        flash('No file selected.', 'danger')
        return redirect(url_for('assets.detail_asset', asset_id=asset_id))

    if not allowed_file(file.filename):
        flash('File type not allowed. Allowed: PDF, DOCX, PPTX, XLSX, TXT', 'danger')
        return redirect(url_for('assets.detail_asset', asset_id=asset_id))

    doc = save_uploaded_file(file, asset_id)
    if doc:
        log_activity(
            current_user.id, current_user.username,
            'Upload File',
            f'Uploaded {doc.original_filename} to asset {asset.asset_tag}'
        )
        flash('File uploaded successfully.', 'success')
    else:
        flash('Error uploading file.', 'danger')

    return redirect(url_for('assets.detail_asset', asset_id=asset_id))
