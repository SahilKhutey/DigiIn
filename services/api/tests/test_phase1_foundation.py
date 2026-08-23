import pytest

from app.core.config import Settings
from app.core.ids import generate_account_id, is_valid_account_id
from app.integrations.auth import DemoAuthProvider


def test_account_id_is_opaque_and_valid():
    account_id = generate_account_id()
    assert is_valid_account_id(account_id)
    assert account_id.startswith("DIN-")
    assert len(account_id) == 18


def test_account_id_rejects_personal_data_shapes():
    assert not is_valid_account_id("DIN-9876543210")
    assert not is_valid_account_id("DIN-1234-5678")
    assert not is_valid_account_id("9876543210")
    assert not is_valid_account_id("DIN-1990-05-14")


def test_account_ids_are_not_deterministic():
    assert generate_account_id() != generate_account_id()


def test_settings_environment_modes():
    dev_settings = Settings(environment="development")
    assert not dev_settings.is_demo
    assert not dev_settings.is_production

    demo_settings = Settings(environment="demo")
    assert demo_settings.is_demo
    assert not demo_settings.is_production

    prod_settings = Settings(environment="production", auth_secret="prod-super-secret-key-2026")
    prod_settings.validate_runtime()
    assert prod_settings.is_production


def test_settings_production_fails_without_secret():
    prod_settings = Settings(environment="production", auth_secret=None)
    with pytest.raises(RuntimeError, match="DIGIIN_AUTH_SECRET is required in production"):
        prod_settings.validate_runtime()


def test_demo_auth_provider_lifecycle():
    provider = DemoAuthProvider()
    challenge_id = provider.send_otp("+91 9876543210")
    assert challenge_id.startswith("otp_ch_")

    subject = provider.verify_otp(challenge_id, "123456")
    assert subject.role == "CITIZEN"
    assert subject.subject_id.startswith("subj_demo_")
    assert is_valid_account_id(subject.account_id)

    with pytest.raises(ValueError, match="Invalid OTP code"):
        provider.verify_otp(challenge_id, "999999")
