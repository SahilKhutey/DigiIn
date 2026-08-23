"""
DigiIn Controlled Pilot & Production Validation — Support Operations Console
Manages pilot support tickets, SLA tracking, and multi-tier escalation (Support -> Ops -> Security/Privacy -> Engineering).
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from typing import Any


class TicketPriority:
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class TicketStatus:
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    WAITING = "WAITING"
    ESCALATED = "ESCALATED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

@dataclass
class SupportTicket:
    id: str
    requester_id: str
    category: str  # "ACCOUNT" | "DOCUMENT" | "VERIFICATION" | "PROOF" | "ORGANIZATION" | "SECURITY" | "PRIVACY"
    priority: str = TicketPriority.NORMAL
    status: str = TicketStatus.OPEN
    subject: str = ""
    description: str = ""
    assigned_tier: str = "TIER_1_SUPPORT"
    created_at: float = field(default_factory=time.time)
    resolved_at: float | None = None
    timeline: list[dict[str, Any]] = field(default_factory=list)

class SupportOperationsService:
    def __init__(self):
        self._tickets: dict[str, SupportTicket] = {}

    def create_ticket(
        self,
        requester_id: str,
        category: str,
        subject: str,
        description: str,
        priority: str = TicketPriority.NORMAL
    ) -> SupportTicket:
        tid = f"tkt_{secrets.token_hex(8)}"
        ticket = SupportTicket(
            id=tid,
            requester_id=requester_id,
            category=category,
            priority=priority,
            subject=subject,
            description=description,
            timeline=[{"timestamp": time.time(), "event": "Ticket created", "actor": requester_id}]
        )
        self._tickets[tid] = ticket
        return ticket

    def escalate_ticket(self, ticket_id: str, target_tier: str, reason: str, actor: str) -> tuple[bool, SupportTicket | None]:
        ticket = self._tickets.get(ticket_id)
        if not ticket:
            return False, None

        ticket.assigned_tier = target_tier
        ticket.status = TicketStatus.ESCALATED
        ticket.timeline.append({
            "timestamp": time.time(),
            "event": f"Escalated to {target_tier}: {reason}",
            "actor": actor
        })
        return True, ticket

    def resolve_ticket(self, ticket_id: str, resolution_note: str, actor: str) -> tuple[bool, SupportTicket | None]:
        ticket = self._tickets.get(ticket_id)
        if not ticket:
            return False, None

        ticket.status = TicketStatus.RESOLVED
        ticket.resolved_at = time.time()
        ticket.timeline.append({
            "timestamp": time.time(),
            "event": f"Resolved: {resolution_note}",
            "actor": actor
        })
        return True, ticket

    def list_open_tickets(self) -> list[SupportTicket]:
        return [t for t in self._tickets.values() if t.status not in (TicketStatus.RESOLVED, TicketStatus.CLOSED)]
