"""
DigiIn Working Product — Unified Notifications & Activity History
Manages in-app notifications and real-time activity timelines for citizen dashboard (/dashboard/activity).
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ActivityItem:
    id: str
    user_id: str
    action: str
    title: str
    details: dict[str, Any]
    timestamp: float = field(default_factory=time.time)

@dataclass
class InAppNotification:
    id: str
    user_id: str
    type: str
    message: str
    read: bool = False
    created_at: float = field(default_factory=time.time)

class ActivityHistoryManager:
    def __init__(self):
        self._activities: list[ActivityItem] = []

    def record_activity(self, user_id: str, action: str, title: str, details: dict[str, Any]) -> ActivityItem:
        aid = f"act_{secrets.token_hex(8)}"
        item = ActivityItem(id=aid, user_id=user_id, action=action, title=title, details=details)
        self._activities.append(item)
        return item

    def get_user_activity(self, user_id: str) -> list[ActivityItem]:
        return [a for a in self._activities if a.user_id == user_id]

class NotificationManager:
    def __init__(self):
        self._notifications: list[InAppNotification] = []

    def send_notification(self, user_id: str, type: str, message: str) -> InAppNotification:
        nid = f"notif_{secrets.token_hex(8)}"
        notif = InAppNotification(id=nid, user_id=user_id, type=type, message=message)
        self._notifications.append(notif)
        return notif

    def get_unread_notifications(self, user_id: str) -> list[InAppNotification]:
        return [n for n in self._notifications if n.user_id == user_id and not n.read]
