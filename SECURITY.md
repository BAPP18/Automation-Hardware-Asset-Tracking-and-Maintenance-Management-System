# Security Policy

## Supported use

This repository is a portfolio/demo implementation of an IT asset and maintenance management system.

For internet-facing or production-like deployments:

- set a strong `SECRET_KEY`;
- set `APP_ENV=production`;
- keep `SEED_DEMO_DATA=false`;
- use HTTPS and `SESSION_COOKIE_SECURE=true`;
- use managed database/storage where persistence matters;
- do not publish uploaded operational documents;
- rotate credentials immediately if demo accounts were ever exposed.

## Important security controls

The application includes:

- password hashing through Werkzeug;
- Flask-Login session handling;
- role-based route protection;
- persistent per-IP and per-account login throttling with temporary lockout;
- CSRF protection for state-changing forms;
- HTTP-only / SameSite cookies and Secure cookies in production;
- Content Security Policy and defensive browser headers;
- upload extension allow-list and maximum request size;
- workbook validation, import bounds, and spreadsheet formula neutralization;
- activity logging;
- production configuration through environment variables.

## Known limitations

Before real enterprise use, add:

- MFA / SSO;
- malware scanning for uploaded files;
- object storage with signed download URLs;
- database migrations;
- centralized logs/monitoring;
- backup/restore procedures;
- fine-grained permissions beyond Admin/Engineer;
- formal secrets management.

## Reporting issues

If you identify a security issue in this portfolio project, avoid publishing sensitive exploit details in a public issue. Contact the repository owner privately when possible.
