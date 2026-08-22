"""Canonical, provider-neutral models for the DigiIn prototype."""

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class TransactionState(StrEnum):
    CREATED = "created"
    AUTHENTICATED = "authenticated"
    CONSENTED = "consented"
    ISSUER_LOOKUP = "issuer_lookup"
    FETCHING = "fetching"
    RECEIVED = "received"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"


class FailureCode(StrEnum):
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    ISSUER_TIMEOUT = "ISSUER_TIMEOUT"
    CALLBACK_FAILED = "CALLBACK_FAILED"
    JOURNEY_COMPLETE = "JOURNEY_COMPLETE"


class DocumentOption(BaseModel):
    id: str
    label: str
    category: str
    trustLabel: Literal["Government issued", "User uploaded", "Pending verification"]


class IssuerHealth(BaseModel):
    issuerId: str
    issuerName: str
    status: Literal["healthy", "degraded", "unavailable"]
    latencyMs: int | None = Field(default=None, ge=0)
    lastCheckedAt: datetime


class TransactionStep(BaseModel):
    name: str
    status: Literal["complete", "attention", "blocked", "not_started"]
    message: str
    owner: str
    nextAction: str | None = None


class RecoveryAction(BaseModel):
    label: str
    type: Literal["retry_later", "correct_record", "return_to_requester", "official_fallback"]
    guidance: str


class TransactionDiagnosis(BaseModel):
    transactionId: str = Field(pattern=r"^[a-z0-9-]{8,64}$")
    documentLabel: str
    trustLabel: Literal["Government issued", "User uploaded", "Pending verification"]
    state: TransactionState
    overallStatus: Literal["resolved", "action_required", "unavailable"]
    issueCode: FailureCode
    issuerStatus: Literal["available", "unavailable", "not_checked"]
    summary: str
    steps: list[TransactionStep]
    recovery: RecoveryAction
    fallbackAvailable: bool
    supportReference: str


class ConsentPreview(BaseModel):
    requesterName: str
    purpose: str
    scopes: list[str]
    access: str
    retentionNotice: str


class ScenarioSummary(BaseModel):
    id: str = Field(pattern=r"^[a-z0-9-]{3,64}$")
    title: str
    description: str
