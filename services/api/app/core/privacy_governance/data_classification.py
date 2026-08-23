"""
DigiIn Privacy & Data Governance — Data Classification & Asset Inventory
Classifies all stored data elements and maintains the central data asset inventory.
"""

from __future__ import annotations

from dataclasses import dataclass


class DataClassification:
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    PERSONAL = "PERSONAL"
    SENSITIVE_PERSONAL = "SENSITIVE_PERSONAL"
    CREDENTIAL = "CREDENTIAL"
    CRYPTOGRAPHIC_SECRET = "CRYPTOGRAPHIC_SECRET"

@dataclass
class DataAsset:
    id: str
    name: str
    classification: str
    purpose: str
    owner: str
    storage_location: str
    retention_policy_id: str
    encryption_profile: str

class DataAssetRegistry:
    def __init__(self):
        self._assets: dict[str, DataAsset] = {}
        self._seed_default_assets()

    def _seed_default_assets(self):
        defaults = [
            DataAsset(
                id="asset_account_profile",
                name="Citizen Account Profile",
                classification=DataClassification.PERSONAL,
                purpose="ACCOUNT_OPERATION",
                owner="DigiIn",
                storage_location="PostgreSQL:users",
                retention_policy_id="RET_ACCOUNT_LIFETIME",
                encryption_profile="AES256_GCM_DB"
            ),
            DataAsset(
                id="asset_uploaded_document",
                name="Citizen Uploaded Evidence Document",
                classification=DataClassification.SENSITIVE_PERSONAL,
                purpose="VERIFICATION",
                owner="Citizen",
                storage_location="S3:digiin-prod-documents-encrypted",
                retention_policy_id="RET_DOC_VERIFICATION_30D",
                encryption_profile="AES256_GCM_STORAGE_ENVELOPE"
            ),
            DataAsset(
                id="asset_verification_claims",
                name="Extracted Verification Claims",
                classification=DataClassification.PERSONAL,
                purpose="VERIFICATION",
                owner="DigiIn",
                storage_location="PostgreSQL:verification_claims",
                retention_policy_id="RET_CLAIMS_7Y",
                encryption_profile="AES256_GCM_DB"
            ),
            DataAsset(
                id="asset_consent_record",
                name="Citizen Consent Record",
                classification=DataClassification.INTERNAL,
                purpose="AUTHORIZATION_EVIDENCE",
                owner="DigiIn",
                storage_location="PostgreSQL:consents",
                retention_policy_id="RET_AUDIT_7Y",
                encryption_profile="AES256_GCM_DB"
            ),
            DataAsset(
                id="asset_signing_key",
                name="Ed25519 Proof Signing Private Key",
                classification=DataClassification.CRYPTOGRAPHIC_SECRET,
                purpose="PROOF_SIGNING",
                owner="DigiIn Root Authority",
                storage_location="CloudKMS_HSM",
                retention_policy_id="RET_INDEFINITE_ACTIVE_ROTATION",
                encryption_profile="HSM_PROTECTED"
            ),
        ]
        for a in defaults:
            self._assets[a.id] = a

    def register_asset(self, asset: DataAsset) -> None:
        self._assets[asset.id] = asset

    def get_asset(self, asset_id: str) -> DataAsset | None:
        return self._assets.get(asset_id)

    def list_assets_by_classification(self, classification: str) -> list[DataAsset]:
        return [a for a in self._assets.values() if a.classification == classification]
