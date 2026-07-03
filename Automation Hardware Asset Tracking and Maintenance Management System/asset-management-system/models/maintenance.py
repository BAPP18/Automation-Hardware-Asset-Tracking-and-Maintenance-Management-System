from datetime import datetime
from models import db


class Maintenance(db.Model):
    __tablename__ = 'maintenance_records'

    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    maintenance_date = db.Column(db.Date, nullable=False)
    engineer = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), nullable=False, default='Scheduled')
    attachment = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Maintenance {self.id} - Asset {self.asset_id}>'
