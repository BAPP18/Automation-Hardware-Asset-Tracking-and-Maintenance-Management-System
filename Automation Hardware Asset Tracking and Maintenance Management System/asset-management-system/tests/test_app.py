import os
import tempfile
import unittest

import openpyxl

from app import create_app
from models import Asset, User, db
from services.export_service import export_assets_excel
from services.import_service import import_assets_from_excel


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
                "LOGIN_MAX_ATTEMPTS": 5,
                "LOGIN_IP_MAX_ATTEMPTS": 25,
                "LOGIN_WINDOW_SECONDS": 600,
                "LOGIN_LOCKOUT_SECONDS": 900,
                "MAX_IMPORT_FILE_SIZE": 1024 * 1024,
                "MAX_IMPORT_ROWS": 100,
            }
        )
        self.client = self.app.test_client()

    def create_user(self, username="admin", role="Admin"):
        with self.app.app_context():
            user = User(
                username=username,
                email=f"{username}@example.test",
                full_name=username.title(),
                role=role,
            )
            user.set_password("CorrectHorseBattery9")
            db.session.add(user)
            db.session.commit()
            return user.id

    def login(self, username="admin", password="CorrectHorseBattery9"):
        return self.client.post(
            "/login",
            data={"username": username, "password": password},
        )

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        self.tempdir.cleanup()

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    def test_security_headers_are_present(self):
        response = self.client.get("/login")
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(response.headers["X-Frame-Options"], "DENY")
        self.assertEqual(
            response.headers["Referrer-Policy"], "strict-origin-when-cross-origin"
        )
        self.assertIn("frame-ancestors 'none'", response.headers["Content-Security-Policy"])
        self.assertIn("script-src 'self' 'nonce-", response.headers["Content-Security-Policy"])
        self.assertNotIn("Strict-Transport-Security", response.headers)

    def test_hsts_is_enabled_in_production(self):
        self.app.config["APP_ENV"] = "production"
        response = self.client.get("/health")
        self.assertEqual(
            response.headers["Strict-Transport-Security"],
            "max-age=31536000; includeSubDomains",
        )

    def test_debug_console_is_not_available(self):
        response = self.client.get("/console")
        self.assertEqual(response.status_code, 404)

    def test_dashboard_requires_authentication(self):
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    def test_demo_users_are_not_seeded_when_disabled(self):
        with self.app.app_context():
            self.assertEqual(User.query.count(), 0)

    def test_login_page_does_not_disclose_demo_passwords(self):
        response = self.client.get("/login")
        self.assertNotIn(b"admin123", response.data)
        self.assertNotIn(b"eng123", response.data)

    def test_login_is_locked_after_five_failures(self):
        self.create_user()
        for attempt in range(4):
            response = self.login(password=f"wrong-password-{attempt}")
            self.assertEqual(response.status_code, 200)

        response = self.login(password="wrong-password-4")
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.headers["Retry-After"], "900")

        response = self.login()
        self.assertEqual(response.status_code, 429)

    def test_engineer_receives_403_for_admin_route(self):
        self.create_user(username="engineer", role="Engineer")
        self.login(username="engineer")
        response = self.client.get("/assets/create")
        self.assertEqual(response.status_code, 403)
        self.assertIn(b"Access denied", response.data)

    def test_logout_requires_post(self):
        self.create_user()
        self.login()
        self.assertEqual(self.client.get("/logout").status_code, 405)
        response = self.client.post("/logout")
        self.assertEqual(response.status_code, 302)

    def test_stored_html_is_escaped(self):
        self.create_user()
        with self.app.app_context():
            asset = Asset(
                asset_tag="XSS-001",
                device_name="<script>alert(1)</script>",
                category="Laptop",
                serial_number="XSS-SERIAL-001",
                status="Available",
                notes="<img src=x onerror=alert(1)>",
            )
            db.session.add(asset)
            db.session.commit()
            asset_id = asset.id

        self.login()
        response = self.client.get(f"/assets/{asset_id}")
        self.assertNotIn(b"<script>alert(1)</script>", response.data)
        self.assertNotIn(b"<img src=x onerror=alert(1)>", response.data)
        self.assertIn(b"&lt;script&gt;alert(1)&lt;/script&gt;", response.data)

    def test_excel_export_neutralizes_formulas(self):
        with self.app.app_context():
            asset = Asset(
                asset_tag="FORMULA-001",
                device_name="=HYPERLINK(\"https://example.test\",\"click\")",
                category="Laptop",
                serial_number="FORMULA-SERIAL-001",
                status="Available",
            )
            db.session.add(asset)
            db.session.commit()
            filepath, _ = export_assets_excel()

            workbook = openpyxl.load_workbook(filepath, data_only=False)
            cell = workbook.active["B2"]
            self.assertEqual(cell.data_type, "s")
            self.assertTrue(cell.value.startswith("'="))
            workbook.close()

    def test_excel_import_rejects_formula_cells(self):
        headers = [
            "Asset Tag", "Device Name", "Category", "Brand", "Model",
            "Serial Number", "Purchase Date", "Warranty Expiration", "Vendor",
            "Assigned User", "Department", "Location", "Status", "Condition", "Notes",
        ]
        filepath = os.path.join(self.tempdir.name, "formula.xlsx")
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.append(headers)
        worksheet.append(["IMPORT-001", "=1+1"] + [""] * 13)
        workbook.save(filepath)
        workbook.close()

        with self.app.app_context():
            imported, errors = import_assets_from_excel(filepath)

        self.assertEqual(imported, 0)
        self.assertIn("Formula cells are not allowed", errors[0])


if __name__ == "__main__":
    unittest.main()
