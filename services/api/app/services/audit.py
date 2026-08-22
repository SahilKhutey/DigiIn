import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.entities import AuditEvent


def audit(
    db: Session,
    user_id: str | None,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> AuditEvent:
    """Record an immutable sovereign audit trail event."""
    event = AuditEvent(
        actor_user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        metadata_json=json.dumps(metadata or {}),
    )
    db.add(event)
    db.commit()
    return event
