"""
DigiIn Core Workflow Engine — Review Queue & Conflict-of-Interest Guard
Manages officer review queues, task assignment, and prevents reviewers from approving their own documents.
"""

import secrets
import time
from typing import Any


class ReviewTaskStatus:
    UNASSIGNED = "UNASSIGNED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"

class ReviewWorkflowEngine:
    def __init__(self):
        self._tasks: dict[str, dict[str, Any]] = {}

    def create_review_task(
        self,
        verification_id: str,
        document_id: str,
        citizen_id: str,
        department: str = "EDUCATION",
        priority: str = "NORMAL"
    ) -> dict[str, Any]:
        task_id = f"rev_{secrets.token_hex(12)}"
        task = {
            "id": task_id,
            "verification_id": verification_id,
            "document_id": document_id,
            "citizen_id": citizen_id,
            "department": department,
            "priority": priority,
            "status": ReviewTaskStatus.UNASSIGNED,
            "assigned_to": None,
            "created_at": time.time(),
            "completed_at": None,
            "decision": None,
            "reason": None,
            "version": 1
        }
        self._tasks[task_id] = task
        return task

    def assign_task(self, task_id: str, reviewer_id: str) -> tuple[bool, str | None]:
        task = self._tasks.get(task_id)
        if not task:
            return False, "TASK_NOT_FOUND"

        # Conflict of Interest check: Reviewer cannot review own document
        if task.get("citizen_id") == reviewer_id:
            return False, "CONFLICT_OF_INTEREST: Reviewer cannot evaluate their own document."

        task["assigned_to"] = reviewer_id
        task["status"] = ReviewTaskStatus.ASSIGNED
        task["version"] = task.get("version", 1) + 1
        return True, None

    def complete_review(
        self,
        task_id: str,
        reviewer_id: str,
        decision: str,  # "APPROVE" | "REJECT" | "ESCALATE"
        reason: str
    ) -> tuple[bool, str | None]:
        task = self._tasks.get(task_id)
        if not task:
            return False, "TASK_NOT_FOUND"

        if task.get("assigned_to") != reviewer_id:
            return False, "FORBIDDEN: Task is not assigned to this reviewer."

        # Conflict of Interest check
        if task.get("citizen_id") == reviewer_id:
            return False, "CONFLICT_OF_INTEREST: Reviewer cannot evaluate their own document."

        if decision == "APPROVE":
            task["status"] = ReviewTaskStatus.APPROVED
        elif decision == "REJECT":
            task["status"] = ReviewTaskStatus.REJECTED
        elif decision == "ESCALATE":
            task["status"] = ReviewTaskStatus.ESCALATED
        else:
            return False, f"INVALID_DECISION: '{decision}' is not a valid review decision."

        task["decision"] = decision
        task["reason"] = reason
        task["completed_at"] = time.time()
        task["version"] = task.get("version", 1) + 1
        return True, None
