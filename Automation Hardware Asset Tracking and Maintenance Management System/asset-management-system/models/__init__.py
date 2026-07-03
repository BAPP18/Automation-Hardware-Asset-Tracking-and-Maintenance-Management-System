from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(session_options={'expire_on_commit': False})

from models.user import User
from models.vendor import Vendor
from models.department import Department
from models.asset import Asset
from models.maintenance import Maintenance
from models.document import Document
from models.activity_log import ActivityLog

__all__ = [
    'db', 'User', 'Vendor', 'Department', 'Asset',
    'Maintenance', 'Document', 'ActivityLog'
]
