from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from config import AES_KEY_SIZE
from utils.exceptions import EncryptionError, DecryptionError


def encrypt_session_key(
    session_key: bytes,
    public_key: rsa.RSAPublicKey,
) -> bytes:
    """
    Encrypt an AES session key using the recipient's RSA public key.
    """

    if not isinstance(session_key, bytes):
        raise EncryptionError("Session key must be bytes.")

    if len(session_key) != AES_KEY_SIZE:
        raise EncryptionError(
            f"Session key must be exactly {AES_KEY_SIZE} bytes."
        )

    if not isinstance(public_key, rsa.RSAPublicKey):
        raise EncryptionError("A valid RSA public key is required.")

    try:
        return public_key.encrypt(
            session_key,
            padding.OAEP(
                mgf=padding.MGF1(
                    algorithm=hashes.SHA256()
                ),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
    except Exception as exc:
        raise EncryptionError(
            "Failed to encrypt session key."
        ) from exc


def decrypt_session_key(
    encrypted_session_key: bytes,
    private_key: rsa.RSAPrivateKey,
) -> bytes:
    """
    Decrypt an AES session key using the recipient's RSA private key.
    """

    if not isinstance(encrypted_session_key, bytes):
        raise DecryptionError(
            "Encrypted session key must be bytes."
        )

    if not isinstance(private_key, rsa.RSAPrivateKey):
        raise DecryptionError(
            "A valid RSA private key is required."
        )

    try:
        session_key = private_key.decrypt(
            encrypted_session_key,
            padding.OAEP(
                mgf=padding.MGF1(
                    algorithm=hashes.SHA256()
                ),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
    except Exception as exc:
        raise DecryptionError(
            "Unable to decrypt session key."
        ) from exc

    if len(session_key) != AES_KEY_SIZE:
        raise DecryptionError(
            f"Invalid decrypted session key size. "
            f"Expected {AES_KEY_SIZE} bytes."
        )

    return session_key