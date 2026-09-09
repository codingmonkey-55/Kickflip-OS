#!/bin/sh
set -eu
BASE=/usr/local/share/kickflip-installer
sudo mkdir -p "$BASE/assets"
sudo cp installer.py kickflip-installer.py "$BASE/"
sudo cp assets/*.png "$BASE/assets/"
sudo sh -c "cat > /usr/local/bin/kickflip-installer <<'EOF'
#!/bin/sh
exec python3 /usr/local/share/kickflip-installer/kickflip-installer.py
EOF"
sudo chmod +x /usr/local/bin/kickflip-installer
sudo cp kickflip-installer.desktop /usr/share/applications/
echo "Installed. Launch with: pkexec kickflip-installer"
