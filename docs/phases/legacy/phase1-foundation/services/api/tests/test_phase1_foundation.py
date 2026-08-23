from app.core.ids import generate_account_id, is_valid_account_id


def test_account_id_is_opaque_and_valid():
    account_id = generate_account_id()
    assert is_valid_account_id(account_id)
    assert account_id.startswith("DIN-")
    assert len(account_id) == 17


def test_account_id_rejects_personal_data_shapes():
    assert not is_valid_account_id("DIN-9876543210")
    assert not is_valid_account_id("DIN-1234-5678")


def test_account_ids_are_not_deterministic():
    assert generate_account_id() != generate_account_id()
