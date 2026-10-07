import os
import tempfile
import unittest

from app import create_app
from models import User, db


class AppSmokeTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        database_path = os.path.join(self.tempdir.name, "test.db")
        upload_path = os.path.join(self.tempdir.name, "uploads")
        export_path = os.path.join(self.tempdir.name, "exports")

        self.app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "test-secret",
                "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path}",
                "UPLOAD_FOLDER": upload_path,
                "EXPORT_FOLDER": export_path,
                "SEED_DEMO_DATA": False,
                "WTF_CSRF_ENABLED": False,
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        self.tempdir.cleanup()

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    def test_dashboard_requires_authentication(self):
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    def test_demo_users_are_not_seeded_when_disabled(self):
        with self.app.app_context():
            self.assertEqual(User.query.count(), 0)


if __name__ == "__main__":
    unittest.main()
