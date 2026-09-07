from pathlib import Path


# ============================================================
# APPLICATION
# ============================================================

APP_NAME = "VeilForge"
VERSION = "v2026.0.1"


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

KEYS_DIR = BASE_DIR / "keys"

PRIVATE_KEY_FILE = KEYS_DIR / "private_key.pem"
PUBLIC_KEY_FILE = KEYS_DIR / "public_key.pem"


# ============================================================
# IMAGE STEGANOGRAPHY
# ============================================================

SUPPORTED_IMAGE_MODE = "RGB"

BITS_PER_CHANNEL = 1

RGB_CHANNELS = 3


# ============================================================
# CRYPTOGRAPHY
# ============================================================

RSA_KEY_SIZE = 3072
RSA_PUBLIC_EXPONENT = 65537

AES_KEY_SIZE = 32
AES_TAG_SIZE = 16
AES_NONCE_SIZE = 12


# ============================================================
# PAYLOAD
# ============================================================

PAYLOAD_MAGIC = b"VF01"
PAYLOAD_VERSION = 1

PAYLOAD_HEADER_SIZE = 14


# ============================================================
# SUPPORTED SECRET TYPES
# ============================================================

TYPE_TEXT = 1

TYPE_TXT_FILE = 2


# ============================================================
# FILE SUPPORT
# ============================================================

SUPPORTED_TEXT_EXTENSION = ".txt"

# ============================================================ 
# SECURITY / VALIDATION LIMITS 
# ============================================================ 

MIN_IMAGE_WIDTH = 1 
MIN_IMAGE_HEIGHT = 1 

MIN_SECRET_SIZE = 1