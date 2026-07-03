from datetime import date, timedelta
from flask import Blueprint, render_template
from flask_login import login_required
from models.asset import Asset
from models.maintenance import Maintenance
from models import db

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    total_assets = Asset.query.count()
    active_assets = Asset.query.filter(Asset.status.in_(['Available', 'Assigned'])).count()
    maintenance_due = Maintenance.query.filter(
        Maintenance.status == 'Scheduled',
        Maintenance.maintenance_date <= date.today()
    ).count()
    retired_assets = Asset.query.filter_by(status='Retired').count()
    assigned_assets = Asset.query.filter_by(status='Assigned').count()

    today = date.today()
    warranty_expired = Asset.query.filter(
        Asset.warranty_expiration.isnot(None),
        Asset.warranty_expiration < today
    ).count()
    warranty_critical = Asset.query.filter(
        Asset.warranty_expiration.isnot(None),
        Asset.warranty_expiration >= today,
        Asset.warranty_expiration <= today + timedelta(days=30)
    ).count()
    warranty_warning = Asset.query.filter(
        Asset.warranty_expiration.isnot(None),
        Asset.warranty_expiration > today + timedelta(days=30),
        Asset.warranty_expiration <= today + timedelta(days=90)
    ).count()

    category_data = db.session.query(
        Asset.category, db.func.count(Asset.id)
    ).group_by(Asset.category).all()
    department_data = db.session.query(
        Asset.department_id,
        db.func.count(Asset.id)
    ).group_by(Asset.department_id).all()
    vendor_data = db.session.query(
        Asset.vendor_id,
        db.func.count(Asset.id)
    ).group_by(Asset.vendor_id).all()

    dept_names = []
    dept_counts = []
    for dept_id, count in department_data:
        if dept_id:
            from models.department import Department
            dept = Department.query.get(dept_id)
            dept_names.append(dept.name if dept else 'Unknown')
            dept_counts.append(count)

    cat_names = [c[0] for c in category_data]
    cat_counts = [c[1] for c in category_data]

    vendor_names = []
    vendor_counts = []
    for vid, count in vendor_data:
        if vid:
            from models.vendor import Vendor
            v = Vendor.query.get(vid)
            vendor_names.append(v.name if v else 'Unknown')
            vendor_counts.append(count)

    return render_template(
        'dashboard.html',
        total_assets=total_assets,
        active_assets=active_assets,
        maintenance_due=maintenance_due,
        retired_assets=retired_assets,
        assigned_assets=assigned_assets,
        warranty_expired=warranty_expired,
        warranty_critical=warranty_critical,
        warranty_warning=warranty_warning,
        cat_names=cat_names,
        cat_counts=cat_counts,
        dept_names=dept_names,
        dept_counts=dept_counts,
        vendor_names=vendor_names,
        vendor_counts=vendor_counts
    )
