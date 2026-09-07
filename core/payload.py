import struct



MAGIC = b"VF01"
VERSION = 1

TYPE_TEXT = 1
TYPE_TXT_FILE = 2

HEADER_FORMAT = "!4sBBQ"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)


def create_header(data_length: int, data_type: int) -> bytes:
    """
    Create a VeilForge payload header.
    """

    if data_length < 0:
        raise ValueError("Data length cannot be negative.")

    if data_type not in (TYPE_TEXT, TYPE_TXT_FILE):
        raise ValueError("Unsupported data type.")

    return struct.pack(
        HEADER_FORMAT,
        MAGIC,
        VERSION,
        data_type,
        data_length,
    )


def parse_header(header: bytes) -> tuple[int, int]:
    """
    Parse and validate a VeilForge payload header.
    """

    if len(header) != HEADER_SIZE:
        raise ValueError(
            f"Invalid header size. Expected {HEADER_SIZE} bytes."
        )

    magic, version, data_type, data_length = struct.unpack(
        HEADER_FORMAT,
        header,
    )

    if magic != MAGIC:
        raise ValueError("Invalid VeilForge payload.")

    if version != VERSION:
        raise ValueError(
            f"Unsupported payload version: {version}"
        )

    if data_type not in (TYPE_TEXT, TYPE_TXT_FILE):
        raise ValueError("Unsupported data type.")

    return data_type, data_length


def create_payload(data: bytes, data_type: int) -> bytes:
    """
    Combine the VeilForge header with payload data.
    """

    header = create_header(len(data), data_type)

    return header + data


def parse_payload(data: bytes) -> tuple[int, bytes]:
    """
    Extract the data type and payload from a complete VeilForge payload.
    """

    if len(data) < HEADER_SIZE:
        raise ValueError("Data is too small to contain a valid header.")

    header = data[:HEADER_SIZE]
    data_type, data_length = parse_header(header)

    payload = data[HEADER_SIZE:]

    if len(payload) != data_length:
        raise ValueError("Payload length does not match header.")

    return data_type, payload
