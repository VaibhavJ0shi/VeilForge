#!/usr/bin/env bash

set -e

INSTALL_DIR="/usr/local/lib/veilforge"
BIN_PATH="/usr/local/bin/veilforge"

echo "======================================"
echo "       VeilForge Uninstaller"
echo "======================================"
echo

if [ "$EUID" -ne 0 ]; then
    echo "Error: Please run the uninstaller with sudo."
    echo
    echo "Usage:"
    echo "  sudo ./uninstall.sh"
    exit 1
fi

echo "[1/2] Removing VeilForge installation..."

if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
    echo "       Removed: $INSTALL_DIR"
else
    echo "       Installation directory not found."
fi

echo

echo "[2/2] Removing VeilForge command..."

if [ -f "$BIN_PATH" ]; then
    rm -f "$BIN_PATH"
    echo "       Removed: $BIN_PATH"
else
    echo "       VeilForge command not found."
fi

echo
echo "======================================"
echo "   VeilForge uninstalled successfully!"
echo "======================================"
echo