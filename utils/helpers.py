def bytes_to_bits(data: bytes) -> list[int]:
    """
    Convert bytes into a list of bits.

    Example:
        b"A" -> [0, 1, 0, 0, 0, 0, 0, 1]
    """

    if not isinstance(data, bytes):
        raise TypeError("Data must be bytes.")

    bits = []

    for byte in data:
        for shift in range(7, -1, -1):
            bits.append((byte >> shift) & 1)

    return bits


def bits_to_bytes(bits: list[int]) -> bytes:
    """
    Convert a list of bits back into bytes.

    The number of bits must be a multiple of 8.
    """

    if not isinstance(bits, list):
        raise TypeError("Bits must be provided as a list.")

    if any(bit not in (0, 1) for bit in bits):
        raise ValueError("Bits must contain only 0 or 1.")

    if len(bits) % 8 != 0:
        raise ValueError(
            "Number of bits must be a multiple of 8."
        )

    result = bytearray()

    for index in range(0, len(bits), 8):
        byte = 0

        for bit in bits[index:index + 8]:
            byte = (byte << 1) | bit

        result.append(byte)

    return bytes(result)