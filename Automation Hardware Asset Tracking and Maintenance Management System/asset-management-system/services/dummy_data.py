import random
from datetime import datetime, date, timedelta
from models import db
from models.user import User
from models.vendor import Vendor
from models.department import Department
from models.asset import Asset
from models.maintenance import Maintenance
from models.activity_log import ActivityLog


def generate_dummy_data():
    if User.query.first():
        return

    users_data = [
        {'username': 'admin', 'email': 'admin@itasset.com', 'full_name': 'Admin Utama', 'role': 'Admin', 'password': 'admin123'},
        {'username': 'engineer1', 'email': 'engineer1@itasset.com', 'full_name': 'Budi Santoso', 'role': 'Engineer', 'password': 'eng123'},
        {'username': 'engineer2', 'email': 'engineer2@itasset.com', 'full_name': 'Siti Rahayu', 'role': 'Engineer', 'password': 'eng123'},
        {'username': 'engineer3', 'email': 'engineer3@itasset.com', 'full_name': 'Ahmad Hidayat', 'role': 'Engineer', 'password': 'eng123'},
        {'username': 'engineer4', 'email': 'engineer4@itasset.com', 'full_name': 'Dewi Lestari', 'role': 'Engineer', 'password': 'eng123'},
        {'username': 'engineer5', 'email': 'engineer5@itasset.com', 'full_name': 'Rudi Hartono', 'role': 'Engineer', 'password': 'eng123'},
        {'username': 'engineer6', 'email': 'engineer6@itasset.com', 'full_name': 'Maya Indah', 'role': 'Engineer', 'password': 'eng123'},
        {'username': 'engineer7', 'email': 'engineer7@itasset.com', 'full_name': 'Agus Wijaya', 'role': 'Engineer', 'password': 'eng123'},
        {'username': 'engineer8', 'email': 'engineer8@itasset.com', 'full_name': 'Rina Marlina', 'role': 'Engineer', 'password': 'eng123'},
        {'username': 'engineer9', 'email': 'engineer9@itasset.com', 'full_name': 'Doni Prasetyo', 'role': 'Engineer', 'password': 'eng123'},
    ]

    for u in users_data:
        user = User(
            username=u['username'],
            email=u['email'],
            full_name=u['full_name'],
            role=u['role']
        )
        user.set_password(u['password'])
        db.session.add(user)
    db.session.flush()

    vendors_data = [
        {'name': 'PT Teknologi Mandiri', 'contact_person': 'Andi', 'phone': '021-5550101', 'email': 'andi@teknologimandiri.co.id'},
        {'name': 'CV Sinar Komputer', 'contact_person': 'Bambang', 'phone': '021-5550202', 'email': 'bambang@sinarkomputer.co.id'},
        {'name': 'PT Data Prima', 'contact_person': 'Cindy', 'phone': '021-5550303', 'email': 'cindy@dataprima.co.id'},
        {'name': 'PT Network Solusi', 'contact_person': 'Dedy', 'phone': '021-5550404', 'email': 'dedy@networksolusi.co.id'},
        {'name': 'CV Maju Bersama', 'contact_person': 'Eka', 'phone': '021-5550505', 'email': 'eka@majubersama.co.id'},
        {'name': 'PT Infrastruktur Digital', 'contact_person': 'Fajar', 'phone': '021-5550606', 'email': 'fajar@infrastrukturdigital.co.id'},
        {'name': 'CV Teknik Informatika', 'contact_person': 'Gita', 'phone': '021-5550707', 'email': 'gita@tekinformatika.co.id'},
        {'name': 'PT Solusi Enterprise', 'contact_person': 'Hadi', 'phone': '021-5550808', 'email': 'hadi@solusienterprise.co.id'},
    ]

    for v in vendors_data:
        vendor = Vendor(**v)
        db.session.add(vendor)
    db.session.flush()

    departments_data = [
        {'name': 'IT Department', 'description': 'Information Technology'},
        {'name': 'Finance', 'description': 'Finance & Accounting'},
        {'name': 'Human Resources', 'description': 'HR Department'},
        {'name': 'Operations', 'description': 'Operations & Logistics'},
        {'name': 'Marketing', 'description': 'Marketing & Sales'},
    ]

    for d in departments_data:
        dept = Department(**d)
        db.session.add(dept)
    db.session.flush()

    categories = ['Laptop', 'Desktop', 'Server', 'Printer', 'Network Device', 'Monitor', 'Tablet', 'Phone']
    brands_by_cat = {
        'Laptop': ['Dell', 'HP', 'Lenovo', 'Apple', 'ASUS', 'Acer'],
        'Desktop': ['Dell', 'HP', 'Lenovo', 'Custom Build'],
        'Server': ['Dell PowerEdge', 'HP ProLiant', 'Lenovo ThinkSystem', 'Supermicro'],
        'Printer': ['HP', 'Canon', 'Epson', 'Brother'],
        'Network Device': ['Cisco', 'MikroTik', 'TP-Link', 'Ubiquiti'],
        'Monitor': ['Dell', 'Samsung', 'LG', 'AOC'],
        'Tablet': ['Apple iPad', 'Samsung Galaxy Tab', 'Microsoft Surface'],
        'Phone': ['iPhone', 'Samsung Galaxy', 'Google Pixel'],
    }
    statuses = ['Available', 'Assigned', 'Maintenance', 'Retired']
    conditions = ['Good', 'Fair', 'Poor']
    locations = ['Jakarta', 'Bandung', 'Surabaya', 'Yogyakarta', 'Semarang', 'Medan', 'Makassar', 'Bali']
    users = ['Andi', 'Budi', 'Citra', 'Dedi', 'Eka', 'Fitri', 'Gunawan', 'Heni', 'Irwan', 'Juni']

    vendors = Vendor.query.all()
    departments = Department.query.all()

    for i in range(1, 51):
        category = random.choice(categories)
        brand = random.choice(brands_by_cat.get(category, ['Generic']))
        purchase_date = date.today() - timedelta(days=random.randint(30, 1095))
        warranty_days = random.choice([0, 15, 45, 120, 180, 365, 730, 1095])
        warranty_exp = purchase_date + timedelta(days=warranty_days) if warranty_days > 0 else None
        status = random.choices(statuses, weights=[30, 40, 20, 10])[0]
        assigned_user = random.choice(users) if status == 'Assigned' else ''

        asset = Asset(
            asset_tag=f'IT-{datetime.now().strftime("%Y")}-{i:04d}',
            device_name=f"{brand} {category} {i}",
            category=category,
            brand=brand,
            model=f'Model-{random.choice(["A", "B", "C", "X", "Z"])}{random.randint(100, 999)}',
            serial_number=f'SN-{random.randint(10000000, 99999999)}',
            purchase_date=purchase_date,
            warranty_expiration=warranty_exp,
            vendor_id=random.choice(vendors).id,
            assigned_user=assigned_user,
            department_id=random.choice(departments).id,
            location=random.choice(locations),
            status=status,
            condition=random.choice(conditions),
            notes=f'Asset #{i} - generated automatically'
        )
        db.session.add(asset)
    db.session.flush()

    assets = Asset.query.all()
    engineers = User.query.filter_by(role='Engineer').all()
    maint_statuses = ['Scheduled', 'Completed']

    for i in range(20):
        asset = random.choice(assets)
        maintenance = Maintenance(
            asset_id=asset.id,
            maintenance_date=date.today() - timedelta(days=random.randint(0, 365)),
            engineer=random.choice(engineers).full_name,
            description=random.choice([
                'Routine check and cleaning',
                'OS reinstallation',
                'Hardware replacement',
                'Software update',
                'Network configuration',
                'Performance optimization',
                'Security patch installation',
                'Data backup verification',
                'BIOS update',
                'Hard drive diagnostics'
            ]),
            status=random.choice(maint_statuses),
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 365))
        )
        db.session.add(maintenance)
    db.session.flush()

    admin_user = User.query.filter_by(username='admin').first()
    log = ActivityLog(
        user_id=admin_user.id,
        username=admin_user.username,
        action='System Init',
        description='System initialized with dummy data',
        timestamp=datetime.utcnow()
    )
    db.session.add(log)

    db.session.commit()
