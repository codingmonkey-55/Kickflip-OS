# Kickflip OS Live-USB GRUB

This package contains a replacement GRUB menu configuration for an Ubuntu-style
live USB. It changes the visible boot choices to Kickflip OS branding.

## Menu

- Kickflip OS
- Install Kickflip OS
- Kickflip OS — Safe Graphics
- Memory Test (memtest86+)
- Memory Test (memtest86+, serial console)
- Reboot
- Power Off

## Important

The exact `vmlinuz`, `initrd`, and memtest paths vary between Ubuntu releases
and ISO builds. Before replacing the ISO's original configuration, verify that
the files exist at the paths referenced by `grub.cfg`.

For modern Ubuntu ISOs, the live boot configuration may also use additional
GRUB files, loopback logic, or EFI-specific configuration. If a menu entry
fails to boot, restore the ISO's original GRUB configuration and adapt the
paths/parameters to that ISO.

This file is intended as the editable starting point for the Kickflip OS
live-USB menu, not as a universal drop-in replacement for every Ubuntu ISO.


## Installer

From a Linux system, mount the Kickflip OS USB and run:

```bash
chmod +x install.sh
sudo ./install.sh /media/$USER/KICKFLIP
```

Or run `sudo ./install.sh` and enter the USB mount point when prompted.

The installer copies the included `grub.cfg` into `boot/grub/grub.cfg` and, when present, also copies it to `EFI/BOOT/grub.cfg`. It does not partition, format, or erase the drive.
