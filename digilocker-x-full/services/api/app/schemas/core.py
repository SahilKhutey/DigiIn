from pydantic import BaseModel, Field

class CredentialCreate(BaseModel):
    credential_type: str = "CLASS_XII"
    issuer_id: str = "MOCK_CBSE"
    holder_name: str
    passing_year: int = Field(ge=1900, le=2100)

class CredentialOut(BaseModel):
    id: str
    credential_type: str
    issuer_id: str
    holder_name: str
    passing_year: int
    status: str
    verification_level: int

class VerificationCreate(BaseModel):
    requester_name: str
    credential_type: str
    purpose: str

class VerificationOut(BaseModel):
    id: str
    requester_name: str
    credential_type: str
    purpose: str
    status: str

class ConsentCreate(BaseModel):
    decision: str = Field(pattern="^(GRANT|DENY)$")

class VerifyOut(BaseModel):
    result: str
    verification_level: int
    reason: str | None = None
    proof_id: str | None = None

class CorrectionCreate(BaseModel):
    issue_type: str
    description: str
    document_id: str | None = None
