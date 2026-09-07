from config import BITS_PER_CHANNEL, RGB_CHANNELS
from utils.exceptions import DecodingError, EncodingError
from utils.logger import get_logger


logger = get_logger("veilforge.image_stego.lsb")


def set_lsb(value: int, bit: int) -> int:
    """
    Set the least significant bit of a channel value.
    """

    if bit not in (0, 1):
        raise EncodingError(
            "LSB value must be either 0 or 1."
        )

    return (value & ~1) | bit


def get_lsb(value: int) -> int:
    """
    Extract the least significant bit from a channel value.
    """

    return value & 1


def embed_bits(image, bits: list[int]):
    """
    Embed bits into an RGB image using LSB steganography.
    """

    if BITS_PER_CHANNEL != 1:
        raise EncodingError(
            "Unsupported bits-per-channel configuration."
        )

    if RGB_CHANNELS != 3:
        raise EncodingError(
            "Unsupported RGB channel configuration."
        )

    if not isinstance(bits, list):
        raise EncodingError(
            "Bits must be provided as a list."
        )

    logger.info(
        "Starting LSB embedding: %d bits.",
        len(bits),
    )

    pixels = image.load()
    width, height = image.size

    bit_index = 0

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]

            channels = [r, g, b]

            for channel_index in range(RGB_CHANNELS):
                if bit_index >= len(bits):
                    pixels[x, y] = tuple(channels)

                    logger.info(
                        "LSB embedding completed: %d bits.",
                        bit_index,
                    )

                    return image

                channels[channel_index] = set_lsb(
                    channels[channel_index],
                    bits[bit_index],
                )

                bit_index += 1

            pixels[x, y] = tuple(channels)

    if bit_index < len(bits):
        logger.error(
            "LSB embedding failed: payload exceeds image capacity."
        )

        raise EncodingError(
            "Payload exceeds image capacity."
        )

    logger.info(
        "LSB embedding completed: %d bits.",
        bit_index,
    )

    return image


def extract_bits(image, count: int) -> list[int]:
    """
    Extract a specified number of LSB bits from an RGB image.
    """

    if BITS_PER_CHANNEL != 1:
        raise DecodingError(
            "Unsupported bits-per-channel configuration."
        )

    if RGB_CHANNELS != 3:
        raise DecodingError(
            "Unsupported RGB channel configuration."
        )

    if not isinstance(count, int):
        raise DecodingError(
            "Bit count must be an integer."
        )

    if count < 0:
        raise DecodingError(
            "Bit count cannot be negative."
        )

    if count == 0:
        return []

    logger.info(
        "Starting LSB extraction: %d bits.",
        count,
    )

    pixels = image.load()
    width, height = image.size

    bits = []

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]

            channels = (r, g, b)

            for channel in channels:
                bits.append(get_lsb(channel))

                if len(bits) == count:
                    logger.info(
                        "LSB extraction completed: %d bits.",
                        len(bits),
                    )

                    return bits

    logger.error(
        "LSB extraction failed: requested bits exceed image capacity."
    )

    raise DecodingError(
        "Required bit count exceeds image capacity."
    )