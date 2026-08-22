from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CredentialCreate(BaseModel):
    credential_type: str
    issuer_id: str
    holder_name: str
    passing_year: int


class CredentialOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    credential_type: str
    issuer_id: str
    holder_name: str
    passing_year: int
    status: str
    verification_level: int
    created_at: datetime


class VerificationCreate(BaseModel):
    requester_name: str
    credential_type: str
    purpose: str


class VerificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    requester_name: str
    user_id: str
    credential_type: str
    purpose: str
    status: str
    created_at: datetime


class ConsentCreate(BaseModel):
    decision: str  # GRANT or DENY


class VerifyOut(BaseModel):
    result: str
    verification_level: int
    reason: str | None = None
    proof_id: str | None = None


class CorrectionCreate(BaseModel):
    issue_type: str
    description: str
    document_id: str | None = None
