from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.assets import assets_bp
from routes.documents import documents_bp
from routes.maintenance import maintenance_bp
from routes.activity_log import activity_bp

__all__ = [
    'auth_bp', 'dashboard_bp', 'assets_bp',
    'documents_bp', 'maintenance_bp', 'activity_bp'
]
