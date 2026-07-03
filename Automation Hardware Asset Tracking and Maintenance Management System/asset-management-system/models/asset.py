from datetime import datetime, date
from models import db


class Asset(db.Model):
    __tablename__ = 'assets'

    id = db.Column(db.Integer, primary_key=True)
    asset_tag = db.Column(db.String(50), unique=True, nullable=False)
    device_name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    brand = db.Column(db.String(80))
    model = db.Column(db.String(80))
    serial_number = db.Column(db.String(100), unique=True)
    purchase_date = db.Column(db.Date)
    warranty_expiration = db.Column(db.Date)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'))
    assigned_user = db.Column(db.String(120))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    location = db.Column(db.String(120))
    status = db.Column(db.String(30), nullable=False, default='Available')
    condition = db.Column(db.String(30), default='Good')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    maintenance_records = db.relationship('Maintenance', backref='asset', lazy=True, cascade='all, delete-orphan')
    documents = db.relationship('Document', backref='asset', lazy=True, cascade='all, delete-orphan')

    @property
    def warranty_status(self):
        if not self.warranty_expiration:
            return 'N/A'
        today = date.today()
        days_left = (self.warranty_expiration - today).days
        if days_left < 0:
            return 'Expired'
        elif days_left <= 30:
            return 'Critical'
        elif days_left <= 90:
            return 'Warning'
        return 'Active'

    @property
    def warranty_days_left(self):
        if not self.warranty_expiration:
            return None
        return (self.warranty_expiration - date.today()).days

    @property
    def is_active(self):
        return self.status in ('Available', 'Assigned')

    def __repr__(self):
        return f'<Asset {self.asset_tag}>'
