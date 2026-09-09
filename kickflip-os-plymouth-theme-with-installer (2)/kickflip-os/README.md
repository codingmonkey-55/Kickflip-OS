# Kickflip OS Plymouth Theme

## Files

- `kickflip-os.plymouth` - Plymouth theme definition
- `kickflip-os.script` - Plymouth script
- `kickflip-os-plymouth-1920x1080.png` - boot artwork

## Install

Copy the theme directory to:

`/usr/share/plymouth/themes/kickflip-os/`

Then set it as the default Plymouth theme:

```bash
sudo plymouth-set-default-theme -R kickflip-os
```

If your distro does not provide `plymouth-set-default-theme`, regenerate the initramfs using your distro's normal initramfs command after installing the theme.

## Manual install

```bash
sudo mkdir -p /usr/share/plymouth/themes/kickflip-os
sudo cp kickflip-os.plymouth kickflip-os.script kickflip-os-plymouth-1920x1080.png   /usr/share/plymouth/themes/kickflip-os/
sudo plymouth-set-default-theme -R kickflip-os
```

## Test without rebooting

A Plymouth test can be run from a virtual terminal with:

```bash
sudo plymouthd --debug
sudo plymouth --show-splash
sleep 5
sudo plymouth quit
```

Note: Plymouth runs very early in boot, so the PNG is deliberately self-contained and the theme avoids external fonts or runtime dependencies.


## Bootable live-system install script

`install-kickflip.sh` is an executable installer intended to run from a booted
Kickflip OS live environment. It installs the Plymouth files, selects the theme
when `plymouth-set-default-theme` is available, and otherwise rebuilds the
initramfs with the available `update-initramfs` or `dracut` command.

From the live environment:

```bash
cd /path/to/kickflip-os
sudo ./install-kickflip.sh
```

The script does **not** repartition or erase disks. It only installs the
Kickflip OS Plymouth theme into the Linux system that is currently running.
