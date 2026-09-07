from PIL import Image
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

from crypto.encryptor import encrypt_data
from image_stego.encoder import encode_image
from utils.exceptions import EncodingError


def encode_secret(
    image: Image.Image,
    data: bytes,
    data_type: int,
    public_key: RSAPublicKey,
) -> Image.Image:
    """
    Encrypt secret data and hide it inside an image.

    Flow:
        Secret data
        -> AES-256-GCM encryption
        -> RSA encryption of AES session key
        -> VeilForge payload
        -> LSB embedding
    """

    if not isinstance(data, bytes):
        raise EncodingError("Secret data must be bytes.")

    if not isinstance(public_key, RSAPublicKey):
        raise EncodingError(
            "A valid RSA public key is required."
        )

    try:
        encrypted_data = encrypt_data(
            data,
            public_key,
        )

        stego_image = encode_image(
            image,
            encrypted_data,
            data_type,
        )

        return stego_image

    except EncodingError:
        raise

    except Exception as exc:
        raise EncodingError(
            "Failed to encode secret data."
        ) from exc