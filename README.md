# IT Asset Tracker & Document Management System

A comprehensive web-based application for managing IT assets, maintenance records, and documents. Built with Python Flask and Bootstrap 5, designed for IT departments to track hardware assets throughout their lifecycle.

## Project Overview

This system enables organizations to:

- Track IT assets from procurement to retirement
- Manage maintenance schedules and history
- Store and organize asset-related documents
- Import/export asset data via Excel
- Monitor warranty status across the organization
- Log all user activities for audit purposes

Built with enterprise-grade architecture while remaining lightweight enough for small to medium IT teams.

## Features

### Asset Management
- Full CRUD operations for IT assets
- 15+ fields per asset including vendor, department, warranty, and assignment tracking
- Status tracking: Available, Assigned, Maintenance, Retired
- Advanced search and filtering by tag, name, serial number, vendor, department, and status

### Dashboard & Analytics
- KPI cards: Total Assets, Active Assets, Maintenance Due, Assigned Assets
- Warranty status visualization with color-coded indicators (Red/Yellow/Green)
- Interactive charts: Assets by Category, Department, and Vendor (using Chart.js)

### Document Management
- Upload documents per asset (PDF, DOCX, PPTX, XLSX, TXT)
- Automatic file information extraction (page count, paragraphs, slides, etc.)
- Download and delete documents

### Maintenance Tracking
- Record and track maintenance activities per asset
- Status: Scheduled / Completed
- Engineer assignment and description logging

### Excel Integration
- Import assets from .xlsx files with automatic vendor/department creation
- Export asset lists and maintenance reports to Excel

### Security & Access Control
- Role-based access: Admin (full access) and Engineer (read + maintenance)
- Session management with Flask-Login
- Complete activity audit log

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python, Flask |
| ORM | SQLAlchemy |
| Database | SQLite |
| Frontend | HTML5, Bootstrap 5, JavaScript |
| Charts | Chart.js |
| Excel | Pandas, Openpyxl |
| Documents | PyPDF2, python-docx, python-pptx |
| Auth | Flask-Login, Werkzeug |

## Installation

### Prerequisites

- Python 3.9+
- pip (Python package installer)

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/asset-management-system.git
cd asset-management-system

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The application will:
1. Create the SQLite database automatically
2. Generate dummy data (50 assets, 8 vendors, 5 departments, etc.)
3. Start the development server at `http://127.0.0.1:5000`

### Default Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Engineer | engineer1 | eng123 |

## Folder Structure

```
asset-management-system/
├── app.py                  # Application entry point
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── database/               # SQLite database file
├── uploads/                # Uploaded documents
├── exports/                # Generated Excel exports
├── screenshots/            # Screenshots for portfolio
├── models/                 # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── user.py
│   ├── vendor.py
│   ├── department.py
│   ├── asset.py
│   ├── maintenance.py
│   ├── document.py
│   └── activity_log.py
├── routes/                 # Flask blueprints
│   ├── __init__.py
│   ├── auth.py
│   ├── dashboard.py
│   ├── assets.py
│   ├── documents.py
│   ├── maintenance.py
│   └── activity_log.py
├── services/               # Business logic
│   ├── __init__.py
│   ├── import_service.py
│   ├── export_service.py
│   ├── file_service.py
│   └── dummy_data.py
├── utils/                  # Utility functions
│   ├── __init__.py
│   ├── helpers.py
│   └── decorators.py
├── templates/              # Jinja2 templates
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── import.html
│   ├── activity_log.html
│   ├── assets/
│   │   ├── list.html
│   │   ├── detail.html
│   │   └── form.html
│   ├── maintenance/
│   │   ├── list.html
│   │   └── form.html
│   └── documents/
└── static/                 # Static assets
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## Screenshots

The `screenshots/` folder is where portfolio screenshots should be placed. Recommended screenshots to capture:

1. **Login Page** - `login.png`
2. **Dashboard** - `dashboard.png` (with KPI cards and charts)
3. **Asset List** - `asset-list.png` (with search/filter interface)
4. **Asset Detail** - `asset-detail.png` (showing documents and maintenance)
5. **Create/Edit Asset** - `asset-form.png`
6. **Maintenance Records** - `maintenance.png`
7. **Import Excel** - `import-excel.png`
8. **Activity Log** - `activity-log.png`

## Future Improvements

- Email notifications for warranty expiration
- QR Code generation for asset labels
- REST API for third-party integration
- LDAP/SSO authentication
- Advanced reporting engine
- Asset depreciation calculation
- Mobile-responsive PWA support
- Multi-language support (i18n)
- Cloud storage integration (S3, Google Drive)
- Barcode scanning via mobile camera

## License

MIT License - see LICENSE file for details.

## Author

Built as a portfolio project demonstrating full-stack development with Python Flask, database design, and enterprise IT asset management domain expertise.



