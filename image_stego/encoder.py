from PIL import Image

from core.capacity import validate_capacity
from core.payload import create_payload
from image_stego.lsb import embed_bits
from image_stego.validator import validate_image
from utils.exceptions import EncodingError
from utils.helpers import bytes_to_bits


def encode_image(
    image: Image.Image,
    data: bytes,
    data_type: int,
) -> Image.Image:
    """
    Create a VeilForge payload and embed it into an RGB image
    using LSB steganography.
    """

    validate_image(image)

    if not isinstance(data, bytes):
        raise EncodingError("Data must be bytes.")

    try:
        payload = create_payload(
            data,
            data_type,
        )

        validate_capacity(
            image,
            len(payload),
        )

        bits = bytes_to_bits(payload)

        return embed_bits(
            image,
            bits,
        )

    except EncodingError:
        raise

    except Exception as exc:
        raise EncodingError(
            "Failed to encode data into image."
        ) from exc