import os
import zipfile

import openpyxl
import pandas as pd
from flask import current_app

from models import db
from models.asset import Asset
from models.vendor import Vendor
from models.department import Department


def _validate_workbook(file_path):
    max_rows = current_app.config['MAX_IMPORT_ROWS']
    max_uncompressed = current_app.config['MAX_IMPORT_FILE_SIZE'] * 10

    try:
        with zipfile.ZipFile(file_path) as archive:
            if sum(item.file_size for item in archive.infolist()) > max_uncompressed:
                return 'The workbook is too large after decompression.'
    except zipfile.BadZipFile:
        return 'The uploaded file is not a valid .xlsx workbook.'

    try:
        workbook = openpyxl.load_workbook(
            file_path,
            read_only=True,
            data_only=False,
            keep_links=False,
        )
        if not workbook.worksheets:
            return 'The workbook does not contain a worksheet.'

        worksheet = workbook.worksheets[0]
        if worksheet.max_row > max_rows + 1:
            return f'The workbook exceeds the {max_rows} row import limit.'

        for row in worksheet.iter_rows():
            for cell in row:
                if cell.data_type == 'f':
                    return 'Formula cells are not allowed in asset imports.'
    except Exception:
        current_app.logger.warning('Rejected unreadable Excel import', exc_info=True)
        return 'The uploaded file could not be read as a valid .xlsx workbook.'
    finally:
        if 'workbook' in locals():
            workbook.close()

    return None


def _text(value, default=''):
    if value is None or pd.isna(value):
        return default
    return str(value).strip()


def import_assets_from_excel(file_path):
    if not os.path.exists(file_path):
        return 0, ['File not found.']

    validation_error = _validate_workbook(file_path)
    if validation_error:
        return 0, [validation_error]

    try:
        df = pd.read_excel(file_path, engine='openpyxl')
    except Exception:
        current_app.logger.warning('Failed to parse Excel import', exc_info=True)
        return 0, ['The uploaded workbook could not be parsed.']

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
            asset_tag = _text(row.get('Asset Tag'))
            if not asset_tag:
                errors.append(f'Row {idx + 2}: Asset Tag is required.')
                continue

            existing = Asset.query.filter_by(asset_tag=asset_tag).first()
            if existing:
                errors.append(f'Row {idx + 2}: Asset Tag "{asset_tag}" already exists.')
                continue

            vendor_name = _text(row.get('Vendor'))
            vendor = None
            if vendor_name:
                vendor = Vendor.query.filter_by(name=vendor_name).first()
                if not vendor:
                    vendor = Vendor(name=vendor_name)
                    db.session.add(vendor)
                    db.session.flush()

            dept_name = _text(row.get('Department'))
            department = None
            if dept_name:
                department = Department.query.filter_by(name=dept_name).first()
                if not department:
                    department = Department(name=dept_name)
                    db.session.add(department)
                    db.session.flush()

            purchase_date = None
            if pd.notna(row.get('Purchase Date')):
                parsed_purchase_date = pd.to_datetime(
                    row['Purchase Date'], errors='coerce'
                )
                if pd.isna(parsed_purchase_date):
                    errors.append(f'Row {idx + 2}: Purchase Date is invalid.')
                    continue
                purchase_date = parsed_purchase_date.date()

            warranty_exp = None
            if pd.notna(row.get('Warranty Expiration')):
                parsed_warranty_exp = pd.to_datetime(
                    row['Warranty Expiration'], errors='coerce'
                )
                if pd.isna(parsed_warranty_exp):
                    errors.append(f'Row {idx + 2}: Warranty Expiration is invalid.')
                    continue
                warranty_exp = parsed_warranty_exp.date()

            asset = Asset(
                asset_tag=asset_tag,
                device_name=_text(row.get('Device Name')),
                category=_text(row.get('Category')),
                brand=_text(row.get('Brand')),
                model=_text(row.get('Model')),
                serial_number=_text(row.get('Serial Number')) or None,
                purchase_date=purchase_date,
                warranty_expiration=warranty_exp,
                vendor_id=vendor.id if vendor else None,
                assigned_user=_text(row.get('Assigned User')),
                department_id=department.id if department else None,
                location=_text(row.get('Location')),
                status=_text(row.get('Status'), 'Available') or 'Available',
                condition=_text(row.get('Condition'), 'Good') or 'Good',
                notes=_text(row.get('Notes'))
            )
            db.session.add(asset)
            imported += 1
        except Exception as e:
            errors.append(f'Row {idx + 2}: {str(e)}')

    db.session.commit()
    return imported, errors
