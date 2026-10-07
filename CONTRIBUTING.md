# Contributing

## Local setup

```bash
git clone https://github.com/BAPP18/Automation-Hardware-Asset-Tracking-and-Maintenance-Management-System.git
cd "Automation-Hardware-Asset-Tracking-and-Maintenance-Management-System/Automation Hardware Asset Tracking and Maintenance Management System/asset-management-system"

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export SECRET_KEY="local-dev-secret"
export SEED_DEMO_DATA=true
python app.py
```

On Windows PowerShell, set environment variables with `$env:KEY="value"`.

## Before committing

Run:

```bash
python -m compileall -q .
python -m unittest discover -s tests -v
```

## Engineering rules

- Keep credentials and generated databases out of Git.
- Add tests for changed behavior.
- Keep route handlers focused; move complex business logic into services.
- Preserve audit logging for operational changes.
- Do not add a new lifecycle status without documenting transition rules.
- Keep deployment configuration environment-driven.
- Update README/PM documentation when scope changes.
