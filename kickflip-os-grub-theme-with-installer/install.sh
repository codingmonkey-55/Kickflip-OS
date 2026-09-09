#!/usr/bin/env bash
set -euo pipefail

# Kickflip OS GRUB Theme Installer
# Installs the included GRUB theme and rebuilds the GRUB configuration.

THEME_NAME="kickflip-os"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
THEME_DIR="/boot/grub/themes/${THEME_NAME}"
GRUB_CFG="/etc/default/grub"

if [[ $EUID -ne 0 ]]; then
    echo "Please run this installer as root:"
    echo "  sudo $0"
    exit 1
fi

echo "== Kickflip OS GRUB Theme Installer =="

# Find a directory containing the theme assets.
THEME_SOURCE=""
for candidate in \
    "$SCRIPT_DIR" \
    "$SCRIPT_DIR/kickflip-os-grub-theme" \
    "$SCRIPT_DIR/theme" \
    "$SCRIPT_DIR/grub-theme"
do
    if [[ -f "$candidate/theme.txt" ]]; then
        THEME_SOURCE="$candidate"
        break
    fi
done

if [[ -z "$THEME_SOURCE" ]]; then
    echo "ERROR: Could not find theme.txt in the installer package."
    exit 1
fi

mkdir -p "$THEME_DIR"
cp -a "$THEME_SOURCE"/. "$THEME_DIR"/

# Ensure GRUB uses the installed theme.
if grep -qE '^GRUB_THEME=' "$GRUB_CFG" 2>/dev/null; then
    sed -i "s|^GRUB_THEME=.*|GRUB_THEME=\"${THEME_DIR}/theme.txt\"|" "$GRUB_CFG"
else
    printf '\nGRUB_THEME="%s/theme.txt"\n' "$THEME_DIR" >> "$GRUB_CFG"
fi

# Rebuild GRUB configuration.
if command -v update-grub >/dev/null 2>&1; then
    update-grub
elif command -v grub-mkconfig >/dev/null 2>&1; then
    if [[ -d /boot/grub ]]; then
        grub-mkconfig -o /boot/grub/grub.cfg
    else
        echo "ERROR: /boot/grub was not found."
        exit 1
    fi
else
    echo "ERROR: Neither update-grub nor grub-mkconfig is installed."
    exit 1
fi

echo
echo "Kickflip OS GRUB theme installed successfully."
echo "Theme: ${THEME_DIR}/theme.txt"
echo "Reboot to see the new GRUB screen."
