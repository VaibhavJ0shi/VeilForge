from config import BITS_PER_CHANNEL, RGB_CHANNELS
from utils.exceptions import CapacityError


def calculate_capacity(image) -> int:
    """
    Calculate the maximum payload capacity of an RGB image.

    Returns:
        Maximum capacity in bytes.
    """

    width, height = image.size

    total_pixels = width * height
    total_bits = (
        total_pixels
        * RGB_CHANNELS
        * BITS_PER_CHANNEL
    )

    return total_bits // 8


def validate_capacity(
    image,
    payload_size: int,
) -> None:
    """
    Validate whether an image can hold the given payload size.
    """

    if not isinstance(payload_size, int):
        raise CapacityError(
            "Payload size must be an integer."
        )

    if payload_size < 0:
        raise CapacityError(
            "Payload size cannot be negative."
        )

    capacity = calculate_capacity(image)

    if payload_size > capacity:
        raise CapacityError(
            f"Payload is too large. "
            f"Maximum capacity: {capacity} bytes, "
            f"required: {payload_size} bytes."
        )