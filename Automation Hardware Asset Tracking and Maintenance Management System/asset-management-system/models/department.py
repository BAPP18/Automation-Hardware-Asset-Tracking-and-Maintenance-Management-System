from models import db


class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)

    assets = db.relationship('Asset', backref='department_rel', lazy=True)

    def __repr__(self):
        return f'<Department {self.name}>'
