import os
import secrets

from flask import Flask, g, jsonify, render_template
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from werkzeug.serving import WSGIRequestHandler

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


class NoVersionRequestHandler(WSGIRequestHandler):
    """Keep the local development server from advertising Werkzeug/Python."""

    def send_response(self, code, message=None):
        self.log_request(code)
        self.send_response_only(code, message)
        self.send_header("Date", self.date_time_string())


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
    login_manager.session_protection = "strong"
    login_manager.init_app(app)

    @app.before_request
    def create_csp_nonce():
        g.csp_nonce = secrets.token_urlsafe(24)

    @app.context_processor
    def security_context():
        return {"csp_nonce": g.get("csp_nonce", "")}

    @app.after_request
    def add_security_headers(response):
        nonce = g.get("csp_nonce", "")
        response.headers["Content-Security-Policy"] = "; ".join(
            [
                "default-src 'self'",
                f"script-src 'self' 'nonce-{nonce}' https://cdn.jsdelivr.net",
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
                "font-src 'self' https://cdn.jsdelivr.net",
                "img-src 'self' data:",
                "connect-src 'self'",
                "object-src 'none'",
                "base-uri 'self'",
                "form-action 'self'",
                "frame-ancestors 'none'",
            ]
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"

        if response.mimetype == "text/html":
            response.headers["Cache-Control"] = "no-store"

        if app.config.get("APP_ENV") == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        return response

    @app.errorhandler(403)
    def forbidden(_error):
        return render_template("errors/403.html"), 403

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
    app.run(
        debug=False,
        use_reloader=False,
        request_handler=NoVersionRequestHandler,
    )
