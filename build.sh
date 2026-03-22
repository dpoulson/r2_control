#!/bin/bash
# 1. Create the structure for the .deb inside a temporary folder
mkdir -p build/DEBIAN
mkdir -p build/opt/r2_control
mkdir -p build/etc/systemd/system
mkdir -p build/etc/apache2/sites-available

# ==========================================
# BUILD 1: LITE PACKAGE (INTERNET REQUIRED)
# ==========================================
# Copy metadata using the lite postinst script
cp packaging/postinst.lite build/DEBIAN/postinst
cp packaging/prerm build/DEBIAN/
chmod +x build/DEBIAN/postinst build/DEBIAN/prerm

# Use sed to create the real control file from your template
# This allows us to inject the version and architecture dynamically
sed "s/{{VERSION}}/1.0/g; s/{{ARCHITECTURE}}/arm64/g" packaging/control.template > build/DEBIAN/control

# Copy your existing code into the /opt/ location
# We exclude the 'build' and '.git' and 'wheels' folders to keep the package small
rsync -av --exclude='build' --exclude='.git' --exclude='.venv' --exclude='venv' --exclude='*.deb' --exclude='wheels' . build/opt/r2_control/

# Copy the existing service files to the system location
cp r2_control.service build/etc/systemd/system/
cp controllers/r2_joy.service build/etc/systemd/system/

cp controllers/www/apache.conf build/etc/apache2/sites-available/000-r2.conf

# Final Build
dpkg-deb --build build r2_control_lite_1.0_arm64.deb

# ==========================================
# BUILD 2: OFFLINE PACKAGE (WHEELS BUNDLED)
# ==========================================
# Swap the metadata to the offline postinst script
cp packaging/postinst.offline build/DEBIAN/postinst
chmod +x build/DEBIAN/postinst

# 6. Generate Pre-Compiled Offline Wheels (Since you build in ARM via QEMU, this produces ARM binaries!)
mkdir -p build/opt/r2_control/wheels
python3 -m pip wheel -w build/opt/r2_control/wheels --pre pygame
python3 -m pip wheel -w build/opt/r2_control/wheels -r requirements.txt

# Final Build
dpkg-deb --build build r2_control_offline_1.0_arm64.deb