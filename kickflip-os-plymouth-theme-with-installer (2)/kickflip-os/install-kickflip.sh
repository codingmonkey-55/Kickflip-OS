#!/usr/bin/env bash
# Kickflip OS - boot/live installer script
# Installs the Kickflip OS Plymouth theme into the currently running Linux system.
# Run from the extracted kickflip-os directory:
#   sudo ./install-kickflip.sh
#
# This script is intended to be run from a bootable Kickflip OS live environment
# or any Debian/Ubuntu-family Linux system containing the theme files.

set -euo pipefail

THEME_NAME="kickflip-os"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
THEME_DIR="/usr/share/plymouth/themes/${THEME_NAME}"

if [[ "${EUID}" -ne 0 ]]; then
    echo "Please run as root:"
    echo "  sudo $0"
    exit 1
fi

required_files=(
    "${SCRIPT_DIR}/kickflip-os.plymouth"
    "${SCRIPT_DIR}/kickflip-os.script"
    "${SCRIPT_DIR}/kickflip-os-plymouth-1920x1080.png"
)

for f in "${required_files[@]}"; do
    if [[ ! -f "$f" ]]; then
        echo "ERROR: Missing required file: $f" >&2
        exit 1
    fi
done

echo "=== Kickflip OS Plymouth Installer ==="
echo "Installing to: ${THEME_DIR}"
echo

mkdir -p "${THEME_DIR}"
install -m 0644 "${SCRIPT_DIR}/kickflip-os.plymouth" "${THEME_DIR}/"
install -m 0644 "${SCRIPT_DIR}/kickflip-os.script" "${THEME_DIR}/"
install -m 0644 "${SCRIPT_DIR}/kickflip-os-plymouth-1920x1080.png" "${THEME_DIR}/"

if command -v plymouth-set-default-theme >/dev/null 2>&1; then
    echo "Setting Kickflip OS as the default Plymouth theme..."
    plymouth-set-default-theme -R "${THEME_NAME}"
elif command -v update-initramfs >/dev/null 2>&1; then
    echo "plymouth-set-default-theme was not found."
    echo "Regenerating the initramfs..."
    update-initramfs -u -k all
elif command -v dracut >/dev/null 2>&1; then
    echo "Regenerating initramfs with dracut..."
    dracut --regenerate-all --force
else
    echo "WARNING: No supported initramfs regeneration command was found."
    echo "The theme files were installed, but the initramfs may need to be rebuilt manually."
fi

echo
echo "Kickflip OS Plymouth theme installed successfully."
echo "Reboot to see the boot splash:"
echo "  systemctl reboot"
