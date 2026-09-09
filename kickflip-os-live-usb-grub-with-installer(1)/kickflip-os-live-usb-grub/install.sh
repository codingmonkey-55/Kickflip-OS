#!/usr/bin/env bash
set -euo pipefail

# Kickflip OS Live USB GRUB Installer
# Installs the included grub.cfg to a mounted Kickflip OS/live USB tree.
# Usage:
#   sudo ./install.sh /media/$USER/KICKFLIP
# If no mount point is supplied, the script asks for one.

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CFG_SOURCE="$SCRIPT_DIR/grub.cfg"

if [[ $EUID -ne 0 ]]; then
  echo "Run this installer with sudo:"
  echo "  sudo $0 [MOUNT_POINT]"
  exit 1
fi

if [[ ! -f "$CFG_SOURCE" ]]; then
  echo "ERROR: grub.cfg was not found next to install.sh."
  exit 1
fi

TARGET="${1:-}"

if [[ -z "$TARGET" ]]; then
  read -r -p "Enter the mounted Kickflip OS USB path: " TARGET
fi

TARGET="${TARGET%/}"

if [[ ! -d "$TARGET" ]]; then
  echo "ERROR: Target mount point does not exist: $TARGET"
  exit 1
fi

# Prevent accidentally targeting the live root filesystem.
if [[ "$TARGET" == "/" ]]; then
  echo "ERROR: Refusing to install to /."
  exit 1
fi

mkdir -p "$TARGET/boot/grub"

cp -f "$CFG_SOURCE" "$TARGET/boot/grub/grub.cfg"

# Also place a copy at the common EFI GRUB location when the directory exists.
if [[ -d "$TARGET/EFI/BOOT" ]]; then
  cp -f "$CFG_SOURCE" "$TARGET/EFI/BOOT/grub.cfg"
fi

sync

echo
echo "Kickflip OS Live USB GRUB configuration installed."
echo "Target: $TARGET"
echo "GRUB config: $TARGET/boot/grub/grub.cfg"
echo
echo "You can now unmount/eject the USB and boot it."
