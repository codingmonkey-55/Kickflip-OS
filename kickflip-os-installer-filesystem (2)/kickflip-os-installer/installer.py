#!/usr/bin/env python3
import os, re, subprocess, tempfile, json
from pathlib import Path

def run(cmd, check=True):
    p = subprocess.run(cmd, text=True, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, check=False)
    if check and p.returncode:
        raise RuntimeError(p.stdout)
    return p.stdout.strip()

def drives():
    data = json.loads(run(["lsblk","-J","-b","-o",
        "PATH,SIZE,TYPE,MODEL,RM,RO,MOUNTPOINTS"]))
    return [d for d in data["blockdevices"]
            if d.get("type")=="disk" and not d.get("rm") and not d.get("ro")]

def size(n):
    n=float(n or 0)
    for u in ("B","KB","MB","GB","TB"):
        if n < 1024 or u=="TB":
            return f"{n:.1f} {u}" if u!="B" else f"{n:.0f} B"
        n/=1024

def part(dev, n):
    return f"{dev}p{n}" if "nvme" in dev or "mmcblk" in dev else f"{dev}{n}"

def install(cfg, progress):
    dev=cfg["drive"]["path"]
    if not re.fullmatch(r"[a-z_][a-z0-9_-]{0,31}", cfg["username"]):
        raise RuntimeError("Invalid username.")
    if cfg["password"] != cfg["password2"] or len(cfg["password"]) < 4:
        raise RuntimeError("Passwords do not match or are too short.")

    p1,p2=part(dev,1),part(dev,2)
    progress("Unmounting old partitions")
    run(["umount","-R",dev],False)
    progress("Creating GPT partition table")
    run(["wipefs","-af",dev]); run(["parted","-s",dev,"mklabel","gpt"])
    run(["parted","-s",dev,"mkpart","ESP","fat32","1MiB","513MiB"])
    run(["parted","-s",dev,"set","1","esp","on"])
    run(["parted","-s",dev,"mkpart","root","ext4","513MiB","100%"])
    run(["partprobe",dev])
    progress("Formatting the drive")
    run(["mkfs.fat","-F","32",p1]); run(["mkfs.ext4","-F","-L","KickflipOS",p2])

    source=Path("/cdrom")
    if not (source/"casper/filesystem.squashfs").exists():
        for candidate in (Path("/run/live/medium"),Path("/media")):
            if (candidate/"casper/filesystem.squashfs").exists():
                source=candidate; break
    squash=source/"casper/filesystem.squashfs"
    if not squash.exists():
        raise RuntimeError("Live image not found: expected /cdrom/casper/filesystem.squashfs")

    with tempfile.TemporaryDirectory(prefix="kickflip-") as td:
        target=Path(td)/"target"; target.mkdir()
        progress("Installing the live system")
        run(["mount",p2,str(target)])
        (target/"boot/efi").mkdir(parents=True)
        run(["mount",p1,str(target/"boot/efi")])
        run(["unsquashfs","-f","-d",str(target),str(squash)])

        progress("Creating the user account")
        run(["chroot",str(target),"useradd","-m","-s","/bin/bash",
             "-c",cfg["full_name"],cfg["username"]])
        run(["chroot",str(target),"bash","-c",
             f"echo {cfg['username']}:{subprocess.list2cmdline([cfg['password']])} | chpasswd"])
        run(["chroot",str(target),"usermod","-aG","sudo",cfg["username"]],False)

        (target/"etc/hostname").write_text(cfg.get("hostname","kickflip")+"\n")
        (target/"etc/fstab").write_text(
            f"LABEL=KickflipOS / ext4 defaults 0 1\n"
            f"{p1} /boot/efi vfat umask=0077 0 1\n")
        progress("Installing GRUB")
        if Path("/sys/firmware/efi").exists():
            run(["chroot",str(target),"grub-install","--target=x86_64-efi",
                 "--efi-directory=/boot/efi","--bootloader-id=KickflipOS","--recheck"])
        else:
            run(["chroot",str(target),"grub-install","--recheck",dev])
        run(["chroot",str(target),"update-grub"],False)

        if cfg.get("wifi_ssid"):
            nm=target/"etc/NetworkManager/system-connections"
            nm.mkdir(parents=True,exist_ok=True)
            con=nm/"kickflip-wifi.nmconnection"
            con.write_text(f"""[connection]
id=Kickflip Wi-Fi
type=wifi
autoconnect=true

[wifi]
ssid={cfg["wifi_ssid"]}
mode=infrastructure

[wifi-security]
key-mgmt=wpa-psk
psk={cfg["wifi_password"]}

[ipv4]
method=auto

[ipv6]
method=auto
""")
            os.chmod(con,0o600)

        progress("Finalizing")
        run(["sync"])
        run(["umount","-R",str(target)],False)
    progress("Installation complete")
