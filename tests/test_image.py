from pathlib import Path

import pytest
from PIL import Image

from core.decoder import decode_secret
from core.encoder import encode_secret
from core.payload import TYPE_TEXT, TYPE_TXT_FILE
from crypto.key_manager import generate_key_pair
from image_stego.decoder import decode_image
from image_stego.encoder import encode_image
from image_stego.validator import validate_image
from utils.exceptions import ValidationError, DecryptionError


# ============================================================
# TEST DATA
# ============================================================

TEST_IMAGE = Image.new(
    "RGB",
    (200, 200),
)

TEST_TEXT = b"Hello VeilForge"

TEST_TXT_DATA = (
    b"This is a VeilForge TXT file test."
)


# ============================================================
# IMAGE STEGO TESTS
# ============================================================

def test_image_text_roundtrip():
    """
    Test basic image steganography using direct text bytes.
    """

    stego_image = encode_image(
        TEST_IMAGE.copy(),
        TEST_TEXT,
        TYPE_TEXT,
    )

    data_type, recovered_data = decode_image(
        stego_image
    )

    assert data_type == TYPE_TEXT
    assert recovered_data == TEST_TEXT


def test_image_txt_roundtrip():
    """
    Test image steganography using TXT file data.
    """

    stego_image = encode_image(
        TEST_IMAGE.copy(),
        TEST_TXT_DATA,
        TYPE_TXT_FILE,
    )

    data_type, recovered_data = decode_image(
        stego_image
    )

    assert data_type == TYPE_TXT_FILE
    assert recovered_data == TEST_TXT_DATA


# ============================================================
# FULL ENCRYPTION + IMAGE TESTS
# ============================================================

def test_full_text_roundtrip():
    """
    Test complete text workflow:

        text
          ↓
        AES-256-GCM
          ↓
        RSA key wrapping
          ↓
        LSB embedding
          ↓
        LSB extraction
          ↓
        RSA key recovery
          ↓
        AES-256-GCM decryption
          ↓
        original text
    """

    private_key, public_key = generate_key_pair()

    stego_image = encode_secret(
        TEST_IMAGE.copy(),
        TEST_TEXT,
        TYPE_TEXT,
        public_key,
    )

    data_type, recovered_data = decode_secret(
        stego_image,
        private_key,
    )

    assert data_type == TYPE_TEXT
    assert recovered_data == TEST_TEXT


def test_full_txt_roundtrip():
    """
    Test complete TXT-file workflow.
    """

    private_key, public_key = generate_key_pair()

    stego_image = encode_secret(
        TEST_IMAGE.copy(),
        TEST_TXT_DATA,
        TYPE_TXT_FILE,
        public_key,
    )

    data_type, recovered_data = decode_secret(
        stego_image,
        private_key,
    )

    assert data_type == TYPE_TXT_FILE
    assert recovered_data == TEST_TXT_DATA


# ============================================================
# WRONG KEY TEST
# ============================================================

def test_wrong_private_key_fails():
    """
    Verify that a different RSA private key
    cannot decrypt the hidden data.
    """

    recipient_private_key, recipient_public_key = (
        generate_key_pair()
    )

    wrong_private_key, _ = generate_key_pair()

    stego_image = encode_secret(
        TEST_IMAGE.copy(),
        TEST_TEXT,
        TYPE_TEXT,
        recipient_public_key,
    )

    with pytest.raises(DecryptionError):
        decode_secret(
            stego_image,
            wrong_private_key,
        )


# ============================================================
# INVALID IMAGE TEST
# ============================================================

def test_non_rgb_image_is_rejected():
    """
    Verify that the image stego layer rejects
    unsupported image modes.
    """

    grayscale_image = Image.new(
        "L",
        (200, 200),
    )

    with pytest.raises(ValidationError):
        encode_image(
            grayscale_image,
            TEST_TEXT,
            TYPE_TEXT,
        )


# ============================================================
# EMPTY DATA TEST
# ============================================================

def test_empty_payload_roundtrip():
    """
    Verify that the image stego layer can preserve
    an empty payload.
    """

    stego_image = encode_image(
        TEST_IMAGE.copy(),
        b"",
        TYPE_TEXT,
    )

    data_type, recovered_data = decode_image(
        stego_image
    )

    assert data_type == TYPE_TEXT
    assert recovered_data == b""


#==========================================================
#==========================================================
#==========================================================
def test_validate_image_accepts_valid_rgb_image():
    image = Image.new("RGB", (100, 100))

    validate_image(image)


def test_validate_image_rejects_none():
    with pytest.raises(ValidationError):
        validate_image(None)


def test_validate_image_rejects_string():
    with pytest.raises(ValidationError):
        validate_image("image.png")


def test_validate_image_rejects_random_object():
    with pytest.raises(ValidationError):
        validate_image(object())


def test_validate_image_rejects_grayscale_image():
    image = Image.new("L", (100, 100))

    with pytest.raises(ValidationError):
        validate_image(image)


def test_validate_image_rejects_rgba_image():
    image = Image.new("RGBA", (100, 100))

    with pytest.raises(ValidationError):
        validate_image(image)


def test_validate_image_rejects_cmyk_image():
    image = Image.new("CMYK", (100, 100))

    with pytest.raises(ValidationError):
        validate_image(image)


def test_validate_image_accepts_minimum_valid_rgb_image():
    image = Image.new("RGB", (1, 1))

    validate_image(image)


#==========================================================
#==========================================================
#==========================================================
from core.capacity import calculate_capacity, validate_capacity
from utils.exceptions import CapacityError


def test_calculate_capacity_for_rgb_image():
    image = Image.new("RGB", (100, 100))

    capacity = calculate_capacity(image)

    assert capacity == 3750


def test_validate_capacity_accepts_zero_payload():
    image = Image.new("RGB", (100, 100))

    validate_capacity(image, 0)


def test_validate_capacity_accepts_exact_capacity():
    image = Image.new("RGB", (100, 100))

    capacity = calculate_capacity(image)

    validate_capacity(image, capacity)


def test_validate_capacity_rejects_one_byte_over_capacity():
    image = Image.new("RGB", (100, 100))

    capacity = calculate_capacity(image)

    with pytest.raises(CapacityError):
        validate_capacity(image, capacity + 1)


def test_validate_capacity_rejects_negative_payload_size():
    image = Image.new("RGB", (100, 100))

    with pytest.raises(CapacityError):
        validate_capacity(image, -1)


def test_validate_capacity_rejects_non_integer_payload_size():
    image = Image.new("RGB", (100, 100))

    with pytest.raises(CapacityError):
        validate_capacity(image, "100")


def test_calculate_capacity_for_minimum_image():
    image = Image.new("RGB", (1, 1))

    capacity = calculate_capacity(image)

    assert capacity == 0


def test_validate_capacity_rejects_payload_for_zero_capacity_image():
    image = Image.new("RGB", (1, 1))

    with pytest.raises(CapacityError):
        validate_capacity(image, 1)


#==========================================================
#==========================================================
#==========================================================
from image_stego.lsb import (
    embed_bits,
    extract_bits,
    get_lsb,
    set_lsb,
)
from utils.exceptions import DecodingError, EncodingError


def test_set_lsb_sets_zero():
    assert set_lsb(100, 0) == 100


def test_set_lsb_sets_one():
    assert set_lsb(100, 1) == 101


def test_set_lsb_clears_existing_one():
    assert set_lsb(101, 0) == 100


def test_set_lsb_rejects_invalid_bit():
    with pytest.raises(EncodingError):
        set_lsb(100, 2)


def test_set_lsb_rejects_negative_bit():
    with pytest.raises(EncodingError):
        set_lsb(100, -1)


def test_get_lsb_returns_zero():
    assert get_lsb(100) == 0


def test_get_lsb_returns_one():
    assert get_lsb(101) == 1


def test_embed_bits_rejects_non_list():
    image = Image.new("RGB", (10, 10))

    with pytest.raises(EncodingError):
        embed_bits(image, "01010101")


def test_embed_bits_rejects_payload_exceeding_capacity():
    image = Image.new("RGB", (1, 1))

    bits = [0, 1, 0, 1]

    with pytest.raises(EncodingError):
        embed_bits(image, bits)


def test_embed_bits_and_extract_bits_roundtrip():
    image = Image.new("RGB", (10, 10))

    bits = [
        1, 0, 1, 0,
        0, 1, 0, 1,
        1, 1, 0, 0,
    ]

    embed_bits(image, bits)

    extracted = extract_bits(image, len(bits))

    assert extracted == bits


def test_extract_bits_zero_count():
    image = Image.new("RGB", (10, 10))

    assert extract_bits(image, 0) == []


def test_extract_bits_rejects_non_integer_count():
    image = Image.new("RGB", (10, 10))

    with pytest.raises(DecodingError):
        extract_bits(image, "10")


def test_extract_bits_rejects_negative_count():
    image = Image.new("RGB", (10, 10))

    with pytest.raises(DecodingError):
        extract_bits(image, -1)


def test_extract_bits_rejects_count_exceeding_capacity():
    image = Image.new("RGB", (1, 1))

    with pytest.raises(DecodingError):
        extract_bits(image, 4)


def test_extract_bits_exact_capacity():
    image = Image.new("RGB", (1, 1))

    bits = [1, 0, 1]

    embed_bits(image, bits)

    extracted = extract_bits(image, 3)

    assert extracted == bits


#==========================================================
#==========================================================
#==========================================================
from core.payload import (
    HEADER_SIZE,
    TYPE_TEXT,
    TYPE_TXT_FILE,
    create_header,
    create_payload,
    parse_header,
    parse_payload,
)
from utils.exceptions import ValidationError


def test_create_payload_and_parse_payload_roundtrip():
    data = b"VeilForge payload test."

    payload = create_payload(
        data,
        TYPE_TEXT,
    )

    data_type, extracted_data = parse_payload(payload)

    assert data_type == TYPE_TEXT
    assert extracted_data == data


def test_payload_rejects_invalid_magic():
    data = b"VeilForge"

    payload = bytearray(
        create_payload(
            data,
            TYPE_TEXT,
        )
    )

    payload[0:4] = b"XXXX"

    with pytest.raises(ValueError):
        parse_payload(bytes(payload))


def test_payload_rejects_invalid_version():
    data = b"VeilForge"

    payload = bytearray(
        create_payload(
            data,
            TYPE_TEXT,
        )
    )

    payload[4] = 99

    with pytest.raises(ValueError):
        parse_payload(bytes(payload))


def test_payload_rejects_invalid_data_type():
    data = b"VeilForge"

    payload = bytearray(
        create_payload(
            data,
            TYPE_TEXT,
        )
    )

    payload[5] = 99

    with pytest.raises(ValueError):
        parse_payload(bytes(payload))


def test_payload_rejects_incorrect_data_length():
    data = b"VeilForge"

    payload = bytearray(
        create_payload(
            data,
            TYPE_TEXT,
        )
    )

    payload[6:14] = (9999).to_bytes(
        8,
        byteorder="big",
    )

    with pytest.raises(ValueError):
        parse_payload(bytes(payload))


def test_payload_rejects_truncated_header():
    with pytest.raises(ValueError):
        parse_payload(b"VF01")


def test_payload_rejects_truncated_data():
    payload = create_payload(
        b"VeilForge",
        TYPE_TEXT,
    )

    truncated_payload = payload[:-1]

    with pytest.raises(ValueError):
        parse_payload(truncated_payload)


def test_payload_rejects_extra_data():
    payload = create_payload(
        b"VeilForge",
        TYPE_TEXT,
    )

    corrupted_payload = payload + b"EXTRA"

    with pytest.raises(ValueError):
        parse_payload(corrupted_payload)


def test_payload_rejects_negative_data_length():
    with pytest.raises(ValueError):
        create_header(
            -1,
            TYPE_TEXT,
        )


def test_payload_rejects_invalid_data_type_on_creation():
    with pytest.raises(ValueError):
        create_header(
            10,
            99,
        )


def test_payload_rejects_invalid_header_size():
    with pytest.raises(ValueError):
        parse_header(
            b"VF01"
        )


def test_payload_supports_txt_file_type():
    data = b"This is a TXT file."

    payload = create_payload(
        data,
        TYPE_TXT_FILE,
    )

    data_type, extracted_data = parse_payload(payload)

    assert data_type == TYPE_TXT_FILE
    assert extracted_data == data


#==========================================================
#==========================================================
#==========================================================
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from config import RSA_PUBLIC_EXPONENT, RSA_KEY_SIZE
from core.decoder import decode_secret
from core.encoder import encode_secret
from core.payload import TYPE_TEXT, TYPE_TXT_FILE
from crypto.key_manager import generate_key_pair
from utils.exceptions import DecryptionError, EncodingError


def test_crypto_image_text_roundtrip():
    image = Image.new("RGB", (200, 200))
    private_key, public_key = generate_key_pair()

    secret = b"VeilForge secure image integration test."

    stego_image = encode_secret(
        image,
        secret,
        TYPE_TEXT,
        public_key,
    )

    data_type, recovered = decode_secret(
        stego_image,
        private_key,
    )

    assert data_type == TYPE_TEXT
    assert recovered == secret


def test_crypto_image_txt_file_roundtrip():
    image = Image.new("RGB", (200, 200))
    private_key, public_key = generate_key_pair()

    secret = (
        b"This represents the contents of a TXT file.\n"
        b"VeilForge integration test."
    )

    stego_image = encode_secret(
        image,
        secret,
        TYPE_TXT_FILE,
        public_key,
    )

    data_type, recovered = decode_secret(
        stego_image,
        private_key,
    )

    assert data_type == TYPE_TXT_FILE
    assert recovered == secret


def test_wrong_private_key_cannot_decrypt():
    image = Image.new("RGB", (200, 200))

    recipient_private_key, recipient_public_key = (
        generate_key_pair()
    )

    wrong_private_key, _ = generate_key_pair()

    secret = b"Secret for the correct recipient."

    stego_image = encode_secret(
        image,
        secret,
        TYPE_TEXT,
        recipient_public_key,
    )

    with pytest.raises(DecryptionError):
        decode_secret(
            stego_image,
            wrong_private_key,
        )


def test_tampered_stego_image_cannot_be_decrypted():
    image = Image.new("RGB", (200, 200))
    private_key, public_key = generate_key_pair()

    secret = b"Tampering must be detected."

    stego_image = encode_secret(
        image,
        secret,
        TYPE_TEXT,
        public_key,
    )

    pixels = stego_image.load()

    r, g, b = pixels[0, 0]

    pixels[0, 0] = (
        r ^ 1,
        g,
        b,
    )

    with pytest.raises(DecryptionError):
        decode_secret(
            stego_image,
            private_key,
        )


def test_recipient_private_key_can_decrypt():
    image = Image.new("RGB", (200, 200))

    recipient_private_key, recipient_public_key = (
        generate_key_pair()
    )

    secret = b"Only the intended recipient should recover this."

    stego_image = encode_secret(
        image,
        secret,
        TYPE_TEXT,
        recipient_public_key,
    )

    data_type, recovered = decode_secret(
        stego_image,
        recipient_private_key,
    )

    assert data_type == TYPE_TEXT
    assert recovered == secret


def test_different_recipient_cannot_decrypt():
    image = Image.new("RGB", (200, 200))

    private_a, public_a = generate_key_pair()
    private_b, public_b = generate_key_pair()

    secret = b"Recipient A only."

    stego_image = encode_secret(
        image,
        secret,
        TYPE_TEXT,
        public_a,
    )

    with pytest.raises(DecryptionError):
        decode_secret(
            stego_image,
            private_b,
        )


def test_encrypted_payload_is_not_plaintext():
    image = Image.new("RGB", (200, 200))
    private_key, public_key = generate_key_pair()

    secret = b"This plaintext must never appear directly."

    stego_image = encode_secret(
        image,
        secret,
        TYPE_TEXT,
        public_key,
    )

    from image_stego.decoder import decode_image

    _, encrypted_payload = decode_image(
        stego_image
    )

    assert secret not in encrypted_payload


def test_each_encoding_uses_fresh_encryption():
    image1 = Image.new("RGB", (200, 200))
    image2 = Image.new("RGB", (200, 200))

    private_key, public_key = generate_key_pair()

    secret = b"Same secret, different encryption."

    stego_image1 = encode_secret(
        image1,
        secret,
        TYPE_TEXT,
        public_key,
    )

    stego_image2 = encode_secret(
        image2,
        secret,
        TYPE_TEXT,
        public_key,
    )

    from image_stego.decoder import decode_image

    _, encrypted1 = decode_image(stego_image1)
    _, encrypted2 = decode_image(stego_image2)

    assert encrypted1 != encrypted2

    assert (
        decode_secret(
            stego_image1,
            private_key,
        )[1]
        == secret
    )

    assert (
        decode_secret(
            stego_image2,
            private_key,
        )[1]
        == secret
    )


def test_encode_rejects_invalid_public_key():
    image = Image.new("RGB", (200, 200))

    with pytest.raises(EncodingError):
        encode_secret(
            image,
            b"Secret",
            TYPE_TEXT,
            "not-a-public-key",
        )


def test_decode_rejects_invalid_private_key():
    image = Image.new("RGB", (200, 200))
    private_key, public_key = generate_key_pair()

    stego_image = encode_secret(
        image,
        b"Secret",
        TYPE_TEXT,
        public_key,
    )

    with pytest.raises(DecryptionError):
        decode_secret(
            stego_image,
            "not-a-private-key",
        )


#==========================================================
#==========================================================
#==========================================================
import tempfile

from core.decoder import decode_secret
from core.encoder import encode_secret
from core.payload import TYPE_TEXT
from crypto.key_manager import generate_key_pair
from storage.file_reader import read_image
from storage.file_writer import write_image


def test_rgb_png_roundtrip():
    image = Image.new("RGB", (200, 200))
    private_key, public_key = generate_key_pair()

    secret = b"PNG format integration test."

    stego_image = encode_secret(
        image,
        secret,
        TYPE_TEXT,
        public_key,
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        path = f"{temp_dir}/stego.png"

        write_image(
            stego_image,
            path,
        )

        loaded_image = read_image(path)

        data_type, recovered = decode_secret(
            loaded_image,
            private_key,
        )

    assert loaded_image.mode == "RGB"
    assert data_type == TYPE_TEXT
    assert recovered == secret


def test_rgb_bmp_roundtrip():
    image = Image.new("RGB", (200, 200))
    private_key, public_key = generate_key_pair()

    secret = b"BMP format integration test."

    stego_image = encode_secret(
        image,
        secret,
        TYPE_TEXT,
        public_key,
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        path = f"{temp_dir}/stego.bmp"

        write_image(
            stego_image,
            path,
        )

        loaded_image = read_image(path)

        data_type, recovered = decode_secret(
            loaded_image,
            private_key,
        )

    assert loaded_image.mode == "RGB"
    assert data_type == TYPE_TEXT
    assert recovered == secret


def test_rgb_jpeg_can_be_read():
    image = Image.new("RGB", (200, 200))

    with tempfile.TemporaryDirectory() as temp_dir:
        path = f"{temp_dir}/image.jpg"

        image.save(
            path,
            format="JPEG",
        )

        loaded_image = read_image(path)

    assert loaded_image.mode == "RGB"
    assert loaded_image.size == (200, 200)


def test_grayscale_image_is_rejected_by_stego_layer():
    image = Image.new("L", (200, 200))

    _, public_key = generate_key_pair()

    with pytest.raises(EncodingError):
        encode_secret(
            image,
            b"Grayscale image test.",
            TYPE_TEXT,
            public_key,
        )


def test_rgba_image_is_rejected_by_stego_layer():
    image = Image.new("RGBA", (200, 200))

    _, public_key = generate_key_pair()

    with pytest.raises(EncodingError):
        encode_secret(
            image,
            b"RGBA image test.",
            TYPE_TEXT,
            public_key,
        )


def test_png_preserves_lsb_payload_after_save_and_reload():
    image = Image.new("RGB", (200, 200))
    private_key, public_key = generate_key_pair()

    secret = b"PNG must preserve the embedded LSB data."

    stego_image = encode_secret(
        image,
        secret,
        TYPE_TEXT,
        public_key,
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        path = f"{temp_dir}/stego.png"

        write_image(
            stego_image,
            path,
        )

        reloaded = read_image(path)

        data_type, recovered = decode_secret(
            reloaded,
            private_key,
        )

    assert data_type == TYPE_TEXT
    assert recovered == secret


def test_jpeg_is_not_used_for_stego_roundtrip():
    image = Image.new("RGB", (200, 200))
    private_key, public_key = generate_key_pair()

    secret = b"JPEG should not be used as a stego carrier."

    stego_image = encode_secret(
        image,
        secret,
        TYPE_TEXT,
        public_key,
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        path = f"{temp_dir}/stego.jpg"

        stego_image.save(
            path,
            format="JPEG",
        )

        loaded_image = read_image(path)

    assert loaded_image.mode == "RGB"

    with pytest.raises(DecryptionError):
        decode_secret(
            loaded_image,
            private_key,
        )