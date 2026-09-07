#!/usr/bin/env bash

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"
INSTALL_DIR="/usr/local/lib/veilforge"
BIN_PATH="/usr/local/bin/veilforge"

echo "======================================"
echo "        VeilForge Installer"
echo "======================================"
echo

if [ "$EUID" -ne 0 ]; then
    echo "Error: Please run the installer with sudo."
    echo
    echo "Usage:"
    echo "  sudo ./install.sh"
    exit 1
fi

REAL_USER="${SUDO_USER:-$USER}"
REAL_HOME="$(eval echo "~$REAL_USER")"

echo "[1/6] Checking Python..."

if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: Python 3 is not installed."
    exit 1
fi

PYTHON_VERSION="$(python3 --version)"
echo "       $PYTHON_VERSION"
echo

echo "[2/6] Creating VeilForge environment..."

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
else
    echo "       Existing .venv found."
fi

echo

echo "[3/6] Installing VeilForge..."

"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install "$PROJECT_DIR"

echo

echo "[4/6] Creating system installation..."

rm -rf "$INSTALL_DIR"

mkdir -p "$INSTALL_DIR"

cp -r "$PROJECT_DIR"/. "$INSTALL_DIR"/

echo

echo "[5/6] Creating VeilForge command..."

cat > "$BIN_PATH" <<EOF
#!/usr/bin/env bash
exec "$INSTALL_DIR/.venv/bin/veilforge" "\$@"
EOF

chmod +x "$BIN_PATH"

echo

echo "[6/6] Fixing ownership..."

chown -R "$REAL_USER:$REAL_USER" "$INSTALL_DIR"

echo
echo "============================================"
echo "=====VeilForge installed successfully!"=====
echo "============================================"
echo
echo "You can now use:"
echo
echo "  veilforge --version"
echo "  veilforge --help"
echo