import os
import pandas as pd
from datetime import datetime
from flask import current_app

from models import db
from models.asset import Asset
from models.vendor import Vendor
from models.department import Department


def import_assets_from_excel(file_path):
    if not os.path.exists(file_path):
        return 0, ['File not found.']

    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        return 0, [f'Error reading file: {str(e)}']

    expected_cols = [
        'Asset Tag', 'Device Name', 'Category', 'Brand', 'Model',
        'Serial Number', 'Purchase Date', 'Warranty Expiration',
        'Vendor', 'Assigned User', 'Department', 'Location',
        'Status', 'Condition', 'Notes'
    ]

    missing = [c for c in expected_cols if c not in df.columns]
    if missing:
        return 0, [f'Missing columns: {", ".join(missing)}']

    imported = 0
    errors = []

    for idx, row in df.iterrows():
        try:
            asset_tag = str(row.get('Asset Tag', '')).strip()
            if not asset_tag:
                errors.append(f'Row {idx + 2}: Asset Tag is required.')
                continue

            existing = Asset.query.filter_by(asset_tag=asset_tag).first()
            if existing:
                errors.append(f'Row {idx + 2}: Asset Tag "{asset_tag}" already exists.')
                continue

            vendor_name = str(row.get('Vendor', '')).strip()
            vendor = None
            if vendor_name:
                vendor = Vendor.query.filter_by(name=vendor_name).first()
                if not vendor:
                    vendor = Vendor(name=vendor_name)
                    db.session.add(vendor)
                    db.session.flush()

            dept_name = str(row.get('Department', '')).strip()
            department = None
            if dept_name:
                department = Department.query.filter_by(name=dept_name).first()
                if not department:
                    department = Department(name=dept_name)
                    db.session.add(department)
                    db.session.flush()

            purchase_date = None
            if pd.notna(row.get('Purchase Date')):
                try:
                    purchase_date = pd.to_datetime(row['Purchase Date']).date()
                except Exception:
                    pass

            warranty_exp = None
            if pd.notna(row.get('Warranty Expiration')):
                try:
                    warranty_exp = pd.to_datetime(row['Warranty Expiration']).date()
                except Exception:
                    pass

            asset = Asset(
                asset_tag=asset_tag,
                device_name=str(row.get('Device Name', '')),
                category=str(row.get('Category', '')),
                brand=str(row.get('Brand', '')),
                model=str(row.get('Model', '')),
                serial_number=str(row.get('Serial Number', '')),
                purchase_date=purchase_date,
                warranty_expiration=warranty_exp,
                vendor_id=vendor.id if vendor else None,
                assigned_user=str(row.get('Assigned User', '')),
                department_id=department.id if department else None,
                location=str(row.get('Location', '')),
                status=str(row.get('Status', 'Available')),
                condition=str(row.get('Condition', 'Good')),
                notes=str(row.get('Notes', ''))
            )
            db.session.add(asset)
            imported += 1
        except Exception as e:
            errors.append(f'Row {idx + 2}: {str(e)}')

    db.session.commit()
    return imported, errors
