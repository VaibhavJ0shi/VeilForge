from PIL import Image

from core.payload import HEADER_SIZE, parse_header
from image_stego.lsb import extract_bits
from image_stego.validator import validate_image
from utils.exceptions import DecodingError
from utils.helpers import bits_to_bytes


def decode_image(
    image: Image.Image,
) -> tuple[int, bytes]:
    """
    Extract a VeilForge payload from an image.

    Returns:
        tuple[int, bytes]:
            Data type and encrypted payload.
    """

    validate_image(image)

    try:
        header_bits = extract_bits(
            image,
            HEADER_SIZE * 8,
        )

        header = bits_to_bytes(header_bits)

        data_type, payload_length = parse_header(
            header
        )

        total_payload_size = (
            HEADER_SIZE + payload_length
        )

        payload_bits = extract_bits(
            image,
            total_payload_size * 8,
        )

        complete_payload = bits_to_bytes(
            payload_bits
        )

        extracted_header = complete_payload[
            :HEADER_SIZE
        ]

        extracted_type, extracted_length = (
            parse_header(extracted_header)
        )

        if extracted_type != data_type:
            raise DecodingError(
                "Payload data type mismatch."
            )

        if extracted_length != payload_length:
            raise DecodingError(
                "Payload length mismatch."
            )

        payload = complete_payload[
            HEADER_SIZE:
        ]

        if len(payload) != payload_length:
            raise DecodingError(
                "Extracted payload length does not match header."
            )

        return data_type, payload

    except DecodingError:
        raise

    except ValueError as exc:
        raise DecodingError(
            f"Invalid VeilForge payload: {exc}"
        ) from exc

    except Exception as exc:
        raise DecodingError(
            "Failed to decode image payload."
        ) from exc