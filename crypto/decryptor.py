from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey

from config import AES_KEY_SIZE, AES_NONCE_SIZE
from crypto.key_exchange import decrypt_session_key
from utils.exceptions import DecryptionError


def decrypt_data(
    encrypted_data: bytes,
    private_key: RSAPrivateKey,
) -> bytes:
    """
    Decrypt VeilForge encrypted data using the recipient's
    RSA private key and AES-256-GCM.
    """

    if not isinstance(encrypted_data, bytes):
        raise DecryptionError(
            "Encrypted data must be bytes."
        )

    if not isinstance(private_key, RSAPrivateKey):
        raise DecryptionError(
            "A valid RSA private key is required."
        )

    rsa_key_size = private_key.key_size // 8

    minimum_size = (
        rsa_key_size
        + AES_NONCE_SIZE
        + 16
    )

    if len(encrypted_data) < minimum_size:
        raise DecryptionError(
            "Encrypted data is too small."
        )

    encrypted_session_key = encrypted_data[
        :rsa_key_size
    ]

    nonce_start = rsa_key_size
    nonce_end = nonce_start + AES_NONCE_SIZE

    nonce = encrypted_data[
        nonce_start:nonce_end
    ]

    ciphertext = encrypted_data[
        nonce_end:
    ]

    try:
        session_key = decrypt_session_key(
            encrypted_session_key,
            private_key,
        )

        if len(session_key) != AES_KEY_SIZE:
            raise DecryptionError(
                "Invalid AES session key size."
            )

        aesgcm = AESGCM(session_key)

        return aesgcm.decrypt(
            nonce,
            ciphertext,
            None,
        )

    except DecryptionError:
        raise

    except Exception as exc:
        raise DecryptionError(
            "Failed to decrypt data."
        ) from exc