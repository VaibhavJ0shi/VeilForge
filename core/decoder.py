from PIL import Image
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey

from crypto.decryptor import decrypt_data
from image_stego.decoder import decode_image
from utils.exceptions import DecryptionError


def decode_secret(
    image: Image.Image,
    private_key: RSAPrivateKey,
) -> tuple[int, bytes]:
    """
    Extract and decrypt hidden secret data from an image.

    Flow:
        LSB extraction
        -> VeilForge payload parsing
        -> RSA session-key decryption
        -> AES-256-GCM decryption
        -> Original secret data
    """

    try:
        data_type, encrypted_data = decode_image(
            image
        )

        decrypted_data = decrypt_data(
            encrypted_data,
            private_key,
        )

        return data_type, decrypted_data

    except DecryptionError:
        raise

    except Exception as exc:
        raise DecryptionError(
            "Failed to decode secret data."
        ) from exc