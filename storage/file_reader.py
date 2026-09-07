from pathlib import Path

from PIL import Image

from utils.exceptions import ValidationError


def read_image(
    file_path: str | Path,
) -> Image.Image:
    """
    Read an image file and return it as a Pillow Image.
    """

    path = Path(file_path)

    if not path.is_file():
        raise ValidationError(
            f"Image file not found: {path}"
        )

    try:
        image = Image.open(path)
        image.load()

        return image

    except Exception as exc:
        raise ValidationError(
            f"Failed to read image: {path}"
        ) from exc


def read_text_file(
    file_path: str | Path,
) -> bytes:
    """
    Read a TXT file and return its contents as UTF-8 bytes.
    """

    path = Path(file_path)

    if not path.is_file():
        raise ValidationError(
            f"TXT file not found: {path}"
        )

    if path.suffix.lower() != ".txt":
        raise ValidationError(
            "Only .txt files are supported."
        )

    try:
        return path.read_bytes()

    except Exception as exc:
        raise ValidationError(
            f"Failed to read TXT file: {path}"
        ) from exc