import os

from flask import Flask, jsonify
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from config import Config
from models import User, db
from routes import (
    activity_bp,
    assets_bp,
    auth_bp,
    dashboard_bp,
    documents_bp,
    maintenance_bp,
)
from services.dummy_data import generate_dummy_data

csrf = CSRFProtect()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    csrf.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please login to access this page."
    login_manager.login_message_category = "warning"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @app.get("/health")
    def health():
        return jsonify(
            status="ok",
            environment=app.config.get("APP_ENV", "unknown"),
        )

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(assets_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(maintenance_bp)
    app.register_blueprint(activity_bp)

    with app.app_context():
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        os.makedirs(app.config["EXPORT_FOLDER"], exist_ok=True)
        db.create_all()

        if app.config.get("SEED_DEMO_DATA") and not User.query.first():
            generate_dummy_data()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=app.config.get("APP_ENV") != "production", use_reloader=False)
