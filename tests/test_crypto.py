import pytest

from crypto.decryptor import decrypt_data
from crypto.encryptor import encrypt_data
from crypto.key_exchange import (
    decrypt_session_key,
    encrypt_session_key,
)
from crypto.key_manager import (
    generate_key_pair,
    load_private_key,
    load_public_key,
    save_private_key,
    save_public_key,
)

from utils.exceptions import DecryptionError, EncryptionError


# ============================================================
# TEST DATA
# ============================================================

TEST_DATA = b"Hello VeilForge"


# ============================================================
# KEY PAIR TEST
# ============================================================

def test_key_pair_generation():
    """
    Verify that RSA private and public keys
    can be generated successfully.
    """

    private_key, public_key = generate_key_pair()

    assert private_key is not None
    assert public_key is not None
    assert private_key.key_size == 3072
    assert public_key.key_size == 3072


# ============================================================
# KEY SAVE / LOAD TEST
# ============================================================

def test_key_save_and_load(tmp_path):
    """
    Verify that RSA keys can be saved and loaded
    correctly from PEM files.
    """

    private_key, public_key = generate_key_pair()

    private_path = tmp_path / "private_key.pem"
    public_path = tmp_path / "public_key.pem"

    save_private_key(
        private_key,
        private_path,
    )

    save_public_key(
        public_key,
        public_path,
    )

    loaded_private_key = load_private_key(
        private_path
    )

    loaded_public_key = load_public_key(
        public_path
    )

    assert loaded_private_key.key_size == 3072
    assert loaded_public_key.key_size == 3072


# ============================================================
# RSA SESSION KEY TEST
# ============================================================

def test_session_key_exchange():
    """
    Verify RSA encryption and decryption
    of the AES session key.
    """

    private_key, public_key = generate_key_pair()

    session_key = b"A" * 32

    encrypted_session_key = encrypt_session_key(
        session_key,
        public_key,
    )

    decrypted_session_key = decrypt_session_key(
        encrypted_session_key,
        private_key,
    )

    assert decrypted_session_key == session_key


# ============================================================
# AES + RSA ENCRYPTION TEST
# ============================================================

def test_encrypt_decrypt_roundtrip():
    """
    Verify complete hybrid encryption:

        plaintext
            ↓
        AES-256-GCM
            ↓
        RSA session-key wrapping
            ↓
        encrypted package
            ↓
        RSA session-key recovery
            ↓
        AES-256-GCM
            ↓
        plaintext
    """

    private_key, public_key = generate_key_pair()

    encrypted_data = encrypt_data(
        TEST_DATA,
        public_key,
    )

    decrypted_data = decrypt_data(
        encrypted_data,
        private_key,
    )

    assert decrypted_data == TEST_DATA


# ============================================================
# WRONG PRIVATE KEY TEST
# ============================================================

def test_wrong_private_key_fails():
    """
    Verify that encrypted data cannot be decrypted
    using an unrelated RSA private key.
    """

    recipient_private_key, recipient_public_key = (
        generate_key_pair()
    )

    wrong_private_key, _ = generate_key_pair()

    encrypted_data = encrypt_data(
        TEST_DATA,
        recipient_public_key,
    )

    with pytest.raises(DecryptionError):
        decrypt_data(
            encrypted_data,
            wrong_private_key,
        )


# ============================================================
# TAMPERED DATA TEST
# ============================================================

def test_tampered_encrypted_data_fails():
    """
    Verify AES-256-GCM authentication detects
    modified encrypted data.
    """

    private_key, public_key = generate_key_pair()

    encrypted_data = bytearray(
        encrypt_data(
            TEST_DATA,
            public_key,
        )
    )

    encrypted_data[-1] ^= 1

    with pytest.raises(DecryptionError):
        decrypt_data(
            bytes(encrypted_data),
            private_key,
        )


# ============================================================
# INVALID SESSION KEY TEST
# ============================================================

def test_invalid_session_key_size():
    """
    Verify that only a 32-byte AES session key
    is accepted.
    """

    _, public_key = generate_key_pair()

    invalid_session_key = b"A" * 16

    with pytest.raises(EncryptionError):
        encrypt_session_key(
            invalid_session_key,
            public_key,
        )