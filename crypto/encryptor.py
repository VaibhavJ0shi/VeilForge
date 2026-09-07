import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

from config import AES_KEY_SIZE, AES_NONCE_SIZE
from crypto.key_exchange import encrypt_session_key
from utils.exceptions import EncryptionError


def encrypt_data(
    data: bytes,
    public_key: RSAPublicKey,
) -> bytes:
    """
    Encrypt secret data using AES-256-GCM and
    encrypt the AES session key using RSA.
    """

    if not isinstance(data, bytes):
        raise EncryptionError("Data must be bytes.")

    if not isinstance(public_key, RSAPublicKey):
        raise EncryptionError(
            "A valid RSA public key is required."
        )

    try:
        session_key = AESGCM.generate_key(
            bit_length=AES_KEY_SIZE * 8
        )

        nonce = os.urandom(AES_NONCE_SIZE)

        aesgcm = AESGCM(session_key)

        ciphertext = aesgcm.encrypt(
            nonce,
            data,
            None,
        )

        encrypted_session_key = encrypt_session_key(
            session_key,
            public_key,
        )

    except EncryptionError:
        raise

    except Exception as exc:
        raise EncryptionError(
            "Failed to encrypt data."
        ) from exc

    return (
        encrypted_session_key
        + nonce
        + ciphertext
    )