# Kickflip OS GRUB 2 Theme

This is a GRUB 2 theme based on the supplied Kickflip OS artwork.

## Install

```bash
sudo mkdir -p /boot/grub/themes/kickflip-os
sudo cp theme.txt background.png select.png /boot/grub/themes/kickflip-os/
```

Edit `/etc/default/grub` and set:

```text
GRUB_THEME="/boot/grub/themes/kickflip-os/theme.txt"
```

Then regenerate GRUB:

### Debian / Ubuntu / Linux Mint

```bash
sudo update-grub
```

### Fedora

```bash
sudo grub2-mkconfig -o /boot/grub2/grub.cfg
```

### Arch Linux

If `/etc/default/grub` is used by your setup:

```bash
sudo grub-mkconfig -o /boot/grub/grub.cfg
```

Reboot to see the theme.

## Notes

- The supplied artwork is 1536x1024.
- The static menu text from the artwork was cleared inside the neon frame so GRUB can draw the real, selectable boot entries.
- The menu selection is a pink bar matching the artwork.
- If your firmware/GRUB resolution differs, GRUB will scale/position the background according to its graphics mode.
