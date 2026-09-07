from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from config import RSA_KEY_SIZE, RSA_PUBLIC_EXPONENT
from utils.exceptions import KeyError


def generate_key_pair():
    """
    Generate an RSA public/private key pair.
    """

    try:
        private_key = rsa.generate_private_key(
            public_exponent=RSA_PUBLIC_EXPONENT,
            key_size=RSA_KEY_SIZE,
        )
    except Exception as exc:
        raise KeyError("Failed to generate RSA key pair.") from exc

    public_key = private_key.public_key()

    return private_key, public_key


def save_private_key(
    private_key,
    file_path: str | Path,
) -> None:
    """
    Save an RSA private key in PEM PKCS8 format.
    """

    if not isinstance(private_key, rsa.RSAPrivateKey):
        raise KeyError("A valid RSA private key is required.")

    path = Path(file_path)

    try:
        path.parent.mkdir(parents=True, exist_ok=True)

        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        path.write_bytes(private_bytes)

    except Exception as exc:
        raise KeyError(
            f"Failed to save private key: {path}"
        ) from exc


def save_public_key(
    public_key,
    file_path: str | Path,
) -> None:
    """
    Save an RSA public key in PEM SubjectPublicKeyInfo format.
    """

    if not isinstance(public_key, rsa.RSAPublicKey):
        raise KeyError("A valid RSA public key is required.")

    path = Path(file_path)

    try:
        path.parent.mkdir(parents=True, exist_ok=True)

        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        path.write_bytes(public_bytes)

    except Exception as exc:
        raise KeyError(
            f"Failed to save public key: {path}"
        ) from exc


def load_private_key(
    file_path: str | Path,
):
    """
    Load an RSA private key from a PEM file.
    """

    path = Path(file_path)

    if not path.is_file():
        raise KeyError(f"Private key not found: {path}")

    try:
        private_key = serialization.load_pem_private_key(
            path.read_bytes(),
            password=None,
        )
    except Exception as exc:
        raise KeyError(
            f"Failed to load private key: {path}"
        ) from exc

    if not isinstance(private_key, rsa.RSAPrivateKey):
        raise KeyError("Loaded key is not an RSA private key.")

    return private_key


def load_public_key(
    file_path: str | Path,
):
    """
    Load an RSA public key from a PEM file.
    """

    path = Path(file_path)

    if not path.is_file():
        raise KeyError(f"Public key not found: {path}")

    try:
        public_key = serialization.load_pem_public_key(
            path.read_bytes()
        )
    except Exception as exc:
        raise KeyError(
            f"Failed to load public key: {path}"
        ) from exc

    if not isinstance(public_key, rsa.RSAPublicKey):
        raise KeyError("Loaded key is not an RSA public key.")

    return public_key