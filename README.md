# VeilForge

**A modular steganography toolkit that combines hidden data with strong encryption.**

VeilForge is a Python-based command-line steganography toolkit designed to securely embed encrypted secret data inside digital media.

The current release focuses on **RGB image steganography using LSB encoding**, with support for hiding direct text messages and `.txt` files.

> **Current version:** `v2026.0.1`
> **Status:** Active Development

---


## ✨ Features

* 🔐 **AES-256-GCM** — Encrypts secret data before it is hidden.
* 🔑 **RSA-3072** — Protects the AES session key using the recipient's public key.
* 🖼️ **Image Steganography** — Hides encrypted data inside RGB images using LSB encoding.
* 📝 **Text Support** — Hide and recover direct text messages.
* 📄 **TXT File Support** — Hide and recover `.txt` files.
* 📦 **Structured Payloads** — Uses a versioned payload format for reliable extraction and validation.
* 💻 **CLI First** — Use VeilForge directly through the `veilforge` command.
* 🧩 **Modular Architecture** — Cryptography, payload handling, storage, and steganography are separated into independent layers.
* 🧪 **Automated Testing** — Image and cryptographic workflows are covered by pytest tests.
* 📋 **Logging & Error Handling** — Centralized logging and custom exception handling are included.

---


## 🔎 Why VeilForge?

Steganography hides the **existence** of information, while encryption protects the **information itself**.

VeilForge combines both:

```text
          Secret Data
               │
               ▼
        AES-256-GCM
          Encryption
               │
               ▼
       Encrypted Secret
               │
               ▼
        VeilForge Payload
               │
               ▼
          LSB Encoding
               │
               ▼
           Stego Image
```

This means that even if the hidden data is extracted from the image, it remains encrypted and requires the appropriate private key for decryption.

---


## 🔐 Security Model

VeilForge uses a **hybrid encryption architecture**.

The actual secret is encrypted with a randomly generated **AES-256 session key**. The session key is then encrypted using the intended recipient's **RSA-3072 public key** with RSA-OAEP and SHA-256.

The recipient uses the corresponding private key to recover the session key and decrypt the secret.

```text
Sender
  │
  │ Recipient's Public Key
  ▼
┌─────────────────────────┐
│     AES-256-GCM         │
│     Secret Encryption   │
└────────────┬────────────┘
             │
             ▼
      Encrypted Secret
             │
             │ AES Session Key
             ▼
      RSA-OAEP / SHA-256
             │
             ▼
    Recipient Public Key
             │
             ▼
       Encrypted Key
             │
             ▼
      VeilForge Payload
             │
             ▼
        LSB Encoding
             │
             ▼
         Stego Image
```

### Recipient-based encryption

If a sender encrypts a message using **Recipient C's public key**, possession of the stego image alone is not enough to decrypt it.

```text
Stego Image
    │
    ├── Recipient A ❌
    ├── Recipient B ❌
    ├── Recipient C ✅
    ├── Recipient D ❌
    └── Recipient E ❌
```

Only Recipient C's corresponding private key can decrypt the secret.

---


## 🖼️ Current Image Support

The current implementation supports:

* RGB images
* 1 LSB per RGB channel
* Direct text messages
* `.txt` files

The theoretical storage capacity of an RGB image is:

```text
(width × height × 3) / 8 bytes
```

The encrypted payload and VeilForge header are included within this capacity.

---


# 🚀 Installation

### Requirements

* Python 3.10+
* Linux recommended
* `sudo` privileges

Clone the repository:

```bash
git clone <repository-url>
cd VeilForge
```

Give the execute permission to the installer:
```bash
chmod +x install.sh
```

Run the installer:

```bash
sudo ./install.sh
```

The installer automatically creates the required isolated Python environment, installs VeilForge and its dependencies, and makes the `veilforge` command available system-wide.

After installation, **no virtual environment activation is required**.

You can use VeilForge directly from any directory:

```bash
veilforge --version
```

```bash
veilforge --help
```

## Uninstallation

To completely remove the system-wide VeilForge installation:

Firstly give the execute permission to the uninstaller:
```bash
chmod +x uninstall.sh
```

```bash
sudo ./uninstall.sh
```

The uninstaller removes the VeilForge installation and its command while leaving your cloned repository untouched.

---


# 💻 CLI Usage

## Help

```bash
veilforge --help
```

## Version

```bash
veilforge --version
```

## CLI Test

```bash
veilforge test
```

---


# 🔑 Key Generation

Generate an RSA-3072 key pair:

```bash
veilforge key generate
```

By default:

```text
keys/
├── private_key.pem
└── public_key.pem
```

**Never share the private key.**

The public key is the key that should be provided to the sender.

Custom paths can be specified:

```bash
veilforge key generate --private keys/private_key.pem --public keys/public_key.pem
```

---


# 📝 Hide Text

Encrypt and hide a text message inside an image:

```bash
veilforge encode image --input input.png --output stego.png --text "Hello VeilForge" --public-key keys/public_key.pem
```

The resulting `stego.png` contains the encrypted message.

---


# 📄 Hide a TXT File

```bash
veilforge encode image --input input.png --output stego.png --text-file secret.txt --public-key keys/public_key.pem
```

Only `.txt` files are currently supported.

---


# 🔓 Decode Text

Use the recipient's private key:

```bash
veilforge decode image --input stego.png --private-key keys/private_key.pem
```

The decrypted message is displayed in the terminal.

---


# 📤 Recover a TXT File

```bash
veilforge decode image --input stego.png --private-key keys/private_key.pem --output recovered.txt
```

The recovered file is written to the specified location.

---


# 🔍 Inspect an Image

Check image properties and possible VeilForge payload information:

```bash
veilforge info image --input input.png
```

This can be used to check the image dimensions, mode, capacity, and whether a VeilForge payload can be detected.

---


# 🏗️ Architecture

VeilForge follows a modular architecture so that each layer has a clearly defined responsibility.

```text
VeilForge
│
├── Core
│   ├── Payload
│   ├── Validation
│   └── Capacity
│
├── Steganography
│   └── Image / LSB
│
├── Cryptography
│   ├── AES-256-GCM
│   └── RSA-3072
│
├── Storage
│   ├── Image
│   └── TXT
│
└── Utilities
    ├── Logging
    └── Exceptions
```

### Project Structure

```text
VeilForge/
│
├── main.py
├── config.py
├── pyproject.toml
├── requirements.txt
├── README.md
├── .gitignore
│
├── core/
│   ├── encoder.py
│   ├── decoder.py
│   ├── capacity.py
│   ├── validator.py
│   └── payload.py
│
├── image_stego/
│   ├── encoder.py
│   ├── decoder.py
│   ├── lsb.py
│   └── validator.py
│
├── crypto/
│   ├── encryptor.py
│   ├── decryptor.py
│   ├── key_manager.py
│   └── key_exchange.py
│
├── storage/
│   ├── file_reader.py
│   └── file_writer.py
│
├── utils/
│   ├── logger.py
│   ├── helpers.py
│   └── exceptions.py
│
└── tests/
    ├── test_image.py
    └── test_crypto.py
```

---


# 🧪 Testing

VeilForge uses **pytest** for automated testing.

Run the image test suite:

```bash
PYTHONPATH=. pytest tests/test_image.py -v
```

Run the cryptography test suite:

```bash
PYTHONPATH=. pytest tests/test_crypto.py -v
```

The current tests cover complete image and cryptographic roundtrip workflows, invalid inputs, incorrect keys, and tampered encrypted data.

---


# 📋 Logging

VeilForge includes a centralized logging system.

Application logs are stored in:

```text
logs/veilforge.log
```

The logger records informational messages to the log file while warnings and errors can also be displayed in the console.

---


# 🛡️ Security Notes

* Keep all private keys confidential.
* Do not commit private keys to version control.
* Share only the recipient's public key with the sender.
* The stego image should not be considered a substitute for secure key management.
* AES-GCM authentication protects encrypted data against undetected modification.
* Losing the corresponding private key may make encrypted data unrecoverable.

---


# ⚠️ Development Status

VeilForge is currently under active development.

The **image steganography, payload, cryptography, storage, validation, and CLI foundations are implemented and tested**.

Video and text steganography are part of the planned architecture but are not yet implemented.

---


# 📜 License

This project is currently under development. License information will be added with the first stable release.

---


## 👤 Author

**Vaibhav Joshi**

VeilForge is being developed as a modular security-focused steganography project.
