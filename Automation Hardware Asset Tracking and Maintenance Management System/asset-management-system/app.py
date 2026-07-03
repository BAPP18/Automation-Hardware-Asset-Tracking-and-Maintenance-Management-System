import os
from flask import Flask
from flask_login import LoginManager

from config import Config
from models import db, User
from routes import auth_bp, dashboard_bp, assets_bp, documents_bp, maintenance_bp, activity_bp
from services.dummy_data import generate_dummy_data


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please login to access this page.'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(assets_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(maintenance_bp)
    app.register_blueprint(activity_bp)

    with app.app_context():
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['EXPORT_FOLDER'], exist_ok=True)
        db.create_all()
        if not User.query.first():
            generate_dummy_data()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, use_reloader=False)
