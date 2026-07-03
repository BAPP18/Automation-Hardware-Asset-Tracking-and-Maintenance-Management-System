import os
from datetime import datetime
import pandas as pd
from flask import current_app

from models.asset import Asset
from models.maintenance import Maintenance


def export_assets_excel():
    assets = Asset.query.order_by(Asset.asset_tag).all()
    data = []
    for a in assets:
        vendor_name = a.vendor_rel.name if a.vendor_rel else ''
        dept_name = a.department_rel.name if a.department_rel else ''
        data.append({
            'Asset Tag': a.asset_tag,
            'Device Name': a.device_name,
            'Category': a.category,
            'Brand': a.brand or '',
            'Model': a.model or '',
            'Serial Number': a.serial_number or '',
            'Purchase Date': a.purchase_date.strftime('%Y-%m-%d') if a.purchase_date else '',
            'Warranty Expiration': a.warranty_expiration.strftime('%Y-%m-%d') if a.warranty_expiration else '',
            'Vendor': vendor_name,
            'Assigned User': a.assigned_user or '',
            'Department': dept_name,
            'Location': a.location or '',
            'Status': a.status,
            'Condition': a.condition or '',
            'Notes': a.notes or ''
        })

    df = pd.DataFrame(data)
    export_dir = current_app.config['EXPORT_FOLDER']
    os.makedirs(export_dir, exist_ok=True)
    filename = f'asset_list_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    filepath = os.path.join(export_dir, filename)
    df.to_excel(filepath, index=False, engine='openpyxl')
    return filepath, filename


def export_maintenance_excel():
    records = Maintenance.query.order_by(Maintenance.maintenance_date.desc()).all()
    data = []
    for m in records:
        data.append({
            'Asset Tag': m.asset.asset_tag if m.asset else '',
            'Device Name': m.asset.device_name if m.asset else '',
            'Date': m.maintenance_date.strftime('%Y-%m-%d') if m.maintenance_date else '',
            'Engineer': m.engineer,
            'Description': m.description,
            'Status': m.status
        })

    df = pd.DataFrame(data)
    export_dir = current_app.config['EXPORT_FOLDER']
    os.makedirs(export_dir, exist_ok=True)
    filename = f'maintenance_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    filepath = os.path.join(export_dir, filename)
    df.to_excel(filepath, index=False, engine='openpyxl')
    return filepath, filename
