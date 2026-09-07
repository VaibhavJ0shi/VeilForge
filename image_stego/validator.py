from PIL import Image

from config import (
    MIN_IMAGE_HEIGHT,
    MIN_IMAGE_WIDTH,
    SUPPORTED_IMAGE_MODE,
)
from utils.exceptions import ValidationError


def validate_image(image: Image.Image) -> None:
    """
    Validate whether an image is supported by VeilForge.
    """

    if not isinstance(image, Image.Image):
        raise ValidationError(
            "Input must be a Pillow Image."
        )

    if image.mode != SUPPORTED_IMAGE_MODE:
        raise ValidationError(
            f"Unsupported image mode: {image.mode}. "
            f"Supported mode: {SUPPORTED_IMAGE_MODE}."
        )

    width, height = image.size

    if width < MIN_IMAGE_WIDTH or height < MIN_IMAGE_HEIGHT:
        raise ValidationError(
            "Image dimensions must be greater than zero."
        )