from pathlib import Path

from PIL import Image

from utils.exceptions import ValidationError


def write_image(
    image: Image.Image,
    file_path: str | Path,
) -> None:
    """
    Write a Pillow Image to disk.
    """

    if not isinstance(image, Image.Image):
        raise ValidationError(
            "Input must be a Pillow Image."
        )

    path = Path(file_path)

    try:
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        image.save(path)

    except Exception as exc:
        raise ValidationError(
            f"Failed to write image: {path}"
        ) from exc


def write_text_file(
    data: bytes,
    file_path: str | Path,
) -> None:
    """
    Write bytes to a TXT file.
    """

    if not isinstance(data, bytes):
        raise ValidationError(
            "TXT data must be bytes."
        )

    path = Path(file_path)

    if path.suffix.lower() != ".txt":
        raise ValidationError(
            "Only .txt files are supported."
        )

    try:
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_bytes(data)

    except Exception as exc:
        raise ValidationError(
            f"Failed to write TXT file: {path}"
        ) from exc