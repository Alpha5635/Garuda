"""Security, hashing, and cryptographic helper utilities."""

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Optional
import bcrypt


def compute_sha256(content: bytes) -> str:
    """Calculate hex digest of SHA-256 hash for binary content."""
    hasher = hashlib.sha256()
    hasher.update(content)
    return hasher.hexdigest()


def canonical_json_dumps(obj: Any) -> str:
    """
    Produce deterministic, canonical JSON string for audit event hashing.
    Keys are sorted, separators are compact, and None is handled consistently.
    """
    if obj is None:
        return ""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def format_iso_timestamp(dt: Any) -> str:
    """Format datetime into a deterministic standard UTC ISO 8601 string."""
    if isinstance(dt, str):
        return dt
    if hasattr(dt, "tzinfo"):
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return str(dt)


def compute_canonical_audit_hash(
    timestamp: Any,
    actor_id: Optional[str],
    action: str,
    entity_type: str,
    entity_id: str,
    before_jsonb: Optional[Any],
    after_jsonb: Optional[Any],
    prev_hash: Optional[str] = None,
) -> str:
    """
    Construct canonical audit event string:
    canonical_event = timestamp | actor | action | entity_type | entity_id | canonical(before) | canonical(after) | prev_hash
    event_hash = SHA-256(canonical_event)
    """
    timestamp_str = format_iso_timestamp(timestamp)
    canonical_before = canonical_json_dumps(before_jsonb)
    canonical_after = canonical_json_dumps(after_jsonb)
    actor_str = str(actor_id) if actor_id else "SYSTEM"
    prev_str = str(prev_hash) if prev_hash else "GENESIS"

    canonical_event = f"{timestamp_str}|{actor_str}|{action}|{entity_type}|{str(entity_id)}|{canonical_before}|{canonical_after}|{prev_str}"
    return hashlib.sha256(canonical_event.encode("utf-8")).hexdigest()


def get_password_hash(password: str) -> str:
    """
    Generate production-safe bcrypt password hash (work factor: 12).
    """
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify plain password against hashed password.
    Supports standard bcrypt hashes ($2b$, $2a$, $2y$) and legacy salted fallback for migration safety.
    """
    if not plain_password or not hashed_password:
        return False

    # Check for standard bcrypt format
    if hashed_password.startswith(("$2b$", "$2a$", "$2y$")):
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8"),
            )
        except Exception:
            return False

    # Legacy salted SHA-256 fallback (for demo compatibility)
    salt = "labelsetu_demo_salt_2026"
    legacy_hash = hashlib.sha256((plain_password + salt).encode("utf-8")).hexdigest()
    return legacy_hash == hashed_password
