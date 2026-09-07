class VeilForgeError(Exception):
    """
    Base exception for all VeilForge errors.
    """


class ValidationError(VeilForgeError):
    """
    Raised when input validation fails.
    """


class CapacityError(VeilForgeError):
    """
    Raised when the carrier cannot hold the payload.
    """


class EncodingError(VeilForgeError):
    """
    Raised when encoding fails.
    """


class DecodingError(VeilForgeError):
    """
    Raised when decoding fails.
    """


class EncryptionError(VeilForgeError):
    """
    Raised when encryption fails.
    """


class DecryptionError(VeilForgeError):
    """
    Raised when decryption fails.
    """


class KeyError(VeilForgeError):
    """
    Raised when key generation, loading, or handling fails.
    """