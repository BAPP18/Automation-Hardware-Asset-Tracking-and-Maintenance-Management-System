from models import db


class Vendor(db.Model):
    __tablename__ = 'vendors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    contact_person = db.Column(db.String(120))
    phone = db.Column(db.String(30))
    email = db.Column(db.String(120))
    address = db.Column(db.Text)

    assets = db.relationship('Asset', backref='vendor_rel', lazy=True)

    def __repr__(self):
        return f'<Vendor {self.name}>'
