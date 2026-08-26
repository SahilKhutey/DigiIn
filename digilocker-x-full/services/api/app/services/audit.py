import json
from sqlalchemy.orm import Session
from app.models.entities import AuditEvent

def audit(db: Session, actor_user_id, action, resource_type, resource_id=None, metadata=None):
    event = AuditEvent(
        actor_user_id=actor_user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        metadata_json=json.dumps(metadata or {}, default=str),
    )
    db.add(event)
    db.commit()
    return event
