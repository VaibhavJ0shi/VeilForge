from pathlib import Path

import typer

from core.capacity import calculate_capacity
from core.decoder import decode_secret
from core.encoder import encode_secret
from core.payload import TYPE_TEXT, TYPE_TXT_FILE
from crypto.key_manager import (
    generate_key_pair,
    load_private_key,
    load_public_key,
    save_private_key,
    save_public_key,
)
from image_stego.decoder import decode_image
from storage.file_reader import read_image, read_text_file
from storage.file_writer import write_image, write_text_file


app = typer.Typer(
    name="veilforge",
    help="VeilForge - Modular Steganography Toolkit",
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]}
)

key_app = typer.Typer(
    help="Generate and manage recipient RSA key pairs.",
    context_settings={"help_option_names": ["-h", "--help"]}
)

encode_app = typer.Typer(
    help="Encode secret data into a carrier medium.",
    context_settings={"help_option_names": ["-h", "--help"]}
)

decode_app = typer.Typer(
    help="Decode hidden data from a stego medium.",
    context_settings={"help_option_names": ["-h", "--help"]}
)

info_app = typer.Typer(
    help="Display information about a carrier or stego medium.",
    context_settings={"help_option_names": ["-h", "--help"]}
)


@app.callback(invoke_without_command=True)
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show the VeilForge version.",
    ),
):
    """VeilForge - Modular Steganography Toolkit."""

    if version:
        typer.echo("VeilForge v2026.0.1")
        raise typer.Exit()


@app.command()
def test():
    """Test the VeilForge CLI."""

    typer.echo("VeilForge CLI is working.")


@key_app.command("generate")
def generate_keys(
    private_key_path: Path = typer.Option(
        Path("keys/private_key.pem"),
        "--private",
        "-p",
        help="Path for the RSA private key.",
    ),
    public_key_path: Path = typer.Option(
        Path("keys/public_key.pem"),
        "--public",
        "-u",
        help="Path for the RSA public key.",
    ),
):
    """
    Generate a new RSA public/private key pair.

    The private key must remain secret.
    The public key can be shared with the sender.
    """

    if private_key_path.exists():
        raise typer.BadParameter(
            f"Private key already exists: {private_key_path}"
        )

    if public_key_path.exists():
        raise typer.BadParameter(
            f"Public key already exists: {public_key_path}"
        )

    private_key, public_key = generate_key_pair()

    save_private_key(
        private_key,
        private_key_path,
    )

    save_public_key(
        public_key,
        public_key_path,
    )

    typer.echo("RSA key pair generated successfully.")
    typer.echo(f"Private key: {private_key_path}")
    typer.echo(f"Public key:  {public_key_path}")
    typer.echo()
    typer.echo(
        "Keep the private key secret."
    )
    typer.echo(
        "Share only the public key with the sender."
    )


@encode_app.command()
def image(
    input_path: Path = typer.Option(
        ...,
        "--input",
        "-i",
        help="Path to the carrier image.",
    ),
    output_path: Path = typer.Option(
        ...,
        "--output",
        "-o",
        help="Path for the output stego image.",
    ),
    text: str | None = typer.Option(
        None,
        "--text",
        "-t",
        help="Secret text to hide.",
    ),
    text_file: Path | None = typer.Option(
        None,
        "--text-file",
        "-tf",
        help="TXT file to hide.",
    ),
    public_key_path: Path = typer.Option(
        ...,
        "--public-key",
        "-k",
        help="Recipient's RSA public key.",
    ),
):
    """
    Encrypt secret data for a recipient and hide it in an image.
    """

    # Step 1 :- Make sure exactly one secret-data source
    #           has been provided.
    if text is None and text_file is None:
        raise typer.BadParameter(
            "Provide either --text or --file."
        )

    if text is not None and text_file is not None:
        raise typer.BadParameter(
            "Use either --text or --file, not both."
        )

    # Step 2 :- Read the carrier image.
    image_data = read_image(input_path)

    # Step 3 :- Convert the image to RGB if required.
    if image_data.mode != "RGB":
        image_data = image_data.convert("RGB")

    # Step 4 :- Read the secret data.
    if text is not None:
        secret_data = text.encode("utf-8")
        data_type = TYPE_TEXT

    else:
        secret_data = read_text_file(text_file)
        data_type = TYPE_TXT_FILE

    # Step 5 :- Load the recipient's public key.
    public_key = load_public_key(
        public_key_path
    )

    # Step 6 :- Encrypt the secret and embed it
    #           into the carrier image.
    stego_image = encode_secret(
        image_data,
        secret_data,
        data_type,
        public_key,
    )

    # Step 7 :- Save the resulting stego image.
    write_image(
        stego_image,
        output_path,
    )

    typer.echo(
        f"Encoding successful: {output_path}"
    )


@decode_app.command()
def image(
    input_path: Path = typer.Option(
        ...,
        "--input",
        "-i",
        help="Path to the stego image.",
    ),
    private_key_path: Path = typer.Option(
        ...,
        "--private-key",
        "-k",
        help="Recipient's RSA private key.",
    ),
    output_path: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Output TXT file path for hidden TXT files.",
    ),
):
    """
    Extract and decrypt hidden data from an image.
    """

    # Step 1 :- Read the stego image.
    image_data = read_image(input_path)

    # Step 2 :- Load the recipient's private key.
    private_key = load_private_key(
        private_key_path
    )

    # Step 3 :- Extract and decrypt the secret.
    data_type, secret_data = decode_secret(
        image_data,
        private_key,
    )

    # Step 4 :- Handle direct text.
    if data_type == TYPE_TEXT:

        try:
            text = secret_data.decode("utf-8")

        except UnicodeDecodeError as exc:
            raise typer.BadParameter(
                "Decoded text is not valid UTF-8."
            ) from exc

        typer.echo("Decoded text:")
        typer.echo(text)

        return

    # Step 5 :- Handle TXT file.
    if data_type == TYPE_TXT_FILE:

        if output_path is None:
            raise typer.BadParameter(
                "Use --output when decoding a TXT file."
            )

        write_text_file(
            secret_data,
            output_path,
        )

        typer.echo(
            f"TXT file extracted successfully: {output_path}"
        )

        return

    # Step 6 :- Reject unknown data types.
    raise typer.BadParameter(
        "Unsupported VeilForge data type."
    )


@info_app.command()
def image(
    input_path: Path = typer.Option(
        ...,
        "--input",
        "-i",
        help="Path to the image.",
    ),
):
    """
    Display information about an image.
    """

    # Step 1 :- Read the image.
    image_data = read_image(input_path)

    # Step 2 :- Get basic image information.
    width, height = image_data.size
    capacity = calculate_capacity(image_data)

    typer.echo(f"Image: {input_path}")
    typer.echo(f"Format: {image_data.format}")
    typer.echo(f"Mode: {image_data.mode}")
    typer.echo(f"Size: {width} x {height}")
    typer.echo(f"Capacity: {capacity} bytes")

    # Step 3 :- Try to detect a VeilForge payload.
    try:
        data_type, encrypted_data = decode_image(
            image_data
        )

        typer.echo(
            "VeilForge payload: detected"
        )
        typer.echo(
            f"Data type: {data_type}"
        )
        typer.echo(
            f"Encrypted payload size: "
            f"{len(encrypted_data)} bytes"
        )

    except (ValueError, IndexError):
        typer.echo(
            "VeilForge payload: not detected"
        )


app.add_typer(
    key_app,
    name="key",
)

app.add_typer(
    encode_app,
    name="encode",
)

app.add_typer(
    decode_app,
    name="decode",
)

app.add_typer(
    info_app,
    name="info",
)


if __name__ == "__main__":
    app()