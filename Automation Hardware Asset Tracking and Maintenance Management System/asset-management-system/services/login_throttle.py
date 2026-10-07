import hashlib
import hmac
from datetime import UTC, datetime, timedelta

from flask import current_app

from models import LoginAttempt, db


def _utcnow():
    return datetime.now(UTC).replace(tzinfo=None)


def _digest(scope, value):
    secret = str(current_app.config["SECRET_KEY"]).encode("utf-8")
    message = f"{scope}:{value}".encode("utf-8")
    return hmac.new(secret, message, hashlib.sha256).hexdigest()


def _keys(ip_address, username):
    normalized_user = (username or "").strip().casefold()
    normalized_ip = ip_address or "unknown"
    return {
        "account": _digest("account", f"{normalized_ip}:{normalized_user}"),
        "ip": _digest("ip", normalized_ip),
    }


def retry_after(ip_address, username, now=None):
    now = now or _utcnow()
    digests = list(_keys(ip_address, username).values())
    attempts = LoginAttempt.query.filter(LoginAttempt.key_digest.in_(digests)).all()
    remaining = [
        int((attempt.locked_until - now).total_seconds()) + 1
        for attempt in attempts
        if attempt.locked_until and attempt.locked_until > now
    ]
    return max(remaining, default=0)


def _record_failure(key_digest, limit, now):
    attempt = LoginAttempt.query.filter_by(key_digest=key_digest).first()
    window = timedelta(seconds=current_app.config["LOGIN_WINDOW_SECONDS"])
    lockout = timedelta(seconds=current_app.config["LOGIN_LOCKOUT_SECONDS"])

    if attempt is None:
        attempt = LoginAttempt(
            key_digest=key_digest,
            failed_attempts=0,
            window_started_at=now,
        )
        db.session.add(attempt)

    if attempt.locked_until and attempt.locked_until > now:
        return int((attempt.locked_until - now).total_seconds()) + 1

    if attempt.window_started_at < now - window:
        attempt.failed_attempts = 0
        attempt.window_started_at = now
        attempt.locked_until = None

    attempt.failed_attempts += 1
    attempt.updated_at = now
    if attempt.failed_attempts >= limit:
        attempt.locked_until = now + lockout
        return int(lockout.total_seconds())
    return 0


def record_failure(ip_address, username, now=None):
    now = now or _utcnow()
    keys = _keys(ip_address, username)
    account_retry = _record_failure(
        keys["account"], current_app.config["LOGIN_MAX_ATTEMPTS"], now
    )
    ip_retry = _record_failure(
        keys["ip"], current_app.config["LOGIN_IP_MAX_ATTEMPTS"], now
    )
    db.session.commit()
    return max(account_retry, ip_retry)


def clear_account_failures(ip_address, username):
    account_key = _keys(ip_address, username)["account"]
    LoginAttempt.query.filter_by(key_digest=account_key).delete()
    db.session.commit()
