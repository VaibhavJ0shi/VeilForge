from PIL import Image

from config import (
    MIN_IMAGE_HEIGHT,
    MIN_IMAGE_WIDTH,
    MIN_SECRET_SIZE,
)
from core.capacity import validate_capacity
from core.payload import parse_payload
from utils.exceptions import CapacityError, ValidationError


def validate_carrier_image(
    image: Image.Image,
) -> None:
    """
    Validate an image used as a VeilForge carrier.
    """

    if not isinstance(image, Image.Image):
        raise ValidationError(
            "Carrier must be a Pillow Image."
        )

    if image.mode != "RGB":
        raise ValidationError(
            "Carrier image must be in RGB mode."
        )

    width, height = image.size

    if (
        width < MIN_IMAGE_WIDTH
        or height < MIN_IMAGE_HEIGHT
    ):
        raise ValidationError(
            "Carrier image must have valid dimensions."
        )


def validate_payload(
    payload: bytes,
) -> None:
    """
    Validate a complete VeilForge payload.
    """

    if not isinstance(payload, bytes):
        raise ValidationError(
            "Payload must be bytes."
        )

    try:
        parse_payload(payload)

    except ValueError as exc:
        raise ValidationError(
            f"Invalid VeilForge payload: {exc}"
        ) from exc


def validate_payload_capacity(
    image: Image.Image,
    payload: bytes,
) -> None:
    """
    Validate carrier image, payload structure,
    and payload capacity.
    """

    validate_carrier_image(image)
    validate_payload(payload)

    try:
        validate_capacity(
            image,
            len(payload),
        )

    except CapacityError:
        raise


def validate_secret_data(
    data: bytes,
) -> None:
    """
    Validate original secret data before encryption.
    """

    if not isinstance(data, bytes):
        raise ValidationError(
            "Secret data must be bytes."
        )

    if len(data) < MIN_SECRET_SIZE:
        raise ValidationError(
            "Secret data cannot be empty."
        )


def validate_encrypted_data(
    data: bytes,
) -> None:
    """
    Validate encrypted data before embedding.
    """

    if not isinstance(data, bytes):
        raise ValidationError(
            "Encrypted data must be bytes."
        )

    if len(data) < MIN_SECRET_SIZE:
        raise ValidationError(
            "Encrypted data cannot be empty."
        )