# Kickflip OS Installer

Complete starter installer for an Ubuntu-style Kickflip OS live image.

## Flow

Welcome → Account → Wi-Fi → Drive selection → Confirm → Install.

## Live-image requirement

The live medium must contain:

    /cdrom/casper/filesystem.squashfs

## Build dependencies

    sudo apt install python3 python3-gi gir1.2-gtk-3.0 network-manager       parted dosfstools e2fsprogs squashfs-tools grub-efi-amd64 grub-pc       efibootmgr

## Put it into the live image

    sudo ./install-to-live-image.sh

Then launch:

    pkexec kickflip-installer

## Important

This installer intentionally performs destructive disk operations. It creates
a GPT disk, an EFI FAT32 partition, an ext4 root partition, extracts the live
filesystem, creates the first user, optionally saves Wi-Fi credentials, and
installs GRUB.

Test it in a VM first. Before shipping a real ISO, adapt the package set,
Secure Boot handling, encryption/swap options, locale/timezone setup, and
hardware detection to the exact Kickflip OS base.
