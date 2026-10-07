from datetime import UTC, datetime

from models import db


def utcnow():
    return datetime.now(UTC).replace(tzinfo=None)


class LoginAttempt(db.Model):
    """Persistent counters used to throttle authentication attempts."""

    __tablename__ = "login_attempts"

    id = db.Column(db.Integer, primary_key=True)
    key_digest = db.Column(db.String(64), unique=True, nullable=False, index=True)
    failed_attempts = db.Column(db.Integer, nullable=False, default=0)
    window_started_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    locked_until = db.Column(db.DateTime)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
    )
