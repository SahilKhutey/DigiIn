from app.core.ids import generate_account_id, is_valid_account_id
from app.core.token_security import (
    generate_refresh_token,
    hash_secret,
    verify_secret,
)


def test_account_id_is_independent_of_identity_data():
    account_id = generate_account_id()
    assert is_valid_account_id(account_id)
    assert "@" not in account_id
    assert account_id.startswith("DIN-")


def test_secret_is_hashed_and_verifiable():
    raw = generate_refresh_token()
    encoded = hash_secret(raw)

    assert raw not in encoded
    assert verify_secret(raw, encoded)
    assert not verify_secret(raw + "x", encoded)


def test_refresh_tokens_are_unpredictable():
    assert generate_refresh_token() != generate_refresh_token()
