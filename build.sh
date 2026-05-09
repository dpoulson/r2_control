#!/bin/bash

# Define versions for the different components
CORE_VERSION="1.1"
SOUNDS_VERSION="1.0"
CONTROLLERS_VERSION="1.0"
ARCH="arm64"

echo "Building R2 Control Packages..."
echo "Core Version: $CORE_VERSION"
echo "Sounds Version: $SOUNDS_VERSION"
echo "Controllers Version: $CONTROLLERS_VERSION"

# Clean up previous builds
rm -rf build build_sounds build_controllers

# ==========================================
# BUILD: SOUNDS PACKAGE
# ==========================================
echo "Building Sounds Package..."
mkdir -p build_sounds/DEBIAN
mkdir -p build_sounds/opt/r2_control/sounds

# Copy sounds
rsync -a sounds/ build_sounds/opt/r2_control/sounds/

# Create control file
sed "s/{{VERSION}}/$SOUNDS_VERSION/g; s/{{ARCHITECTURE}}/all/g" packaging/control_sounds.template > build_sounds/DEBIAN/control

# Final Build
dpkg-deb --build build_sounds "r2_control_sounds_${SOUNDS_VERSION}_all.deb"

# ==========================================
# BUILD: CONTROLLERS PACKAGE
# ==========================================
echo "Building Controllers Package..."
mkdir -p build_controllers/DEBIAN
mkdir -p build_controllers/opt/r2_control/controllers
mkdir -p build_controllers/etc/systemd/system
mkdir -p build_controllers/etc/apache2/sites-available

# Copy controllers and associated service/config files
rsync -a controllers/ build_controllers/opt/r2_control/controllers/
cp controllers/r2_joy.service build_controllers/etc/systemd/system/
cp controllers/ble/r2_ble.service build_controllers/etc/systemd/system/
cp controllers/www/apache.conf build_controllers/etc/apache2/sites-available/000-r2.conf

# Setup package scripts
sed "s/{{VERSION}}/$CONTROLLERS_VERSION/g; s/{{ARCHITECTURE}}/$ARCH/g" packaging/control_controllers.template > build_controllers/DEBIAN/control
cp packaging/postinst_controllers build_controllers/DEBIAN/postinst
cp packaging/prerm_controllers build_controllers/DEBIAN/prerm
chmod +x build_controllers/DEBIAN/postinst build_controllers/DEBIAN/prerm

# Final Build
dpkg-deb --build build_controllers "r2_control_controllers_${CONTROLLERS_VERSION}_${ARCH}.deb"

# ==========================================
# BUILD 1: LITE PACKAGE (INTERNET REQUIRED)
# ==========================================
echo "Building Core Lite Package..."
mkdir -p build/DEBIAN
mkdir -p build/opt/r2_control
mkdir -p build/etc/systemd/system
mkdir -p build/etc/udev/rules.d

# Copy metadata using the lite postinst script
cp packaging/postinst.lite build/DEBIAN/postinst
cp packaging/prerm build/DEBIAN/
chmod +x build/DEBIAN/postinst build/DEBIAN/prerm

# Use sed to create the real control file from your template
sed "s/{{VERSION}}/$CORE_VERSION/g; s/{{ARCHITECTURE}}/$ARCH/g" packaging/control.template > build/DEBIAN/control

# Copy your existing code into the /opt/ location
# Exclude sounds and controllers since they are in their own packages
rsync -av --exclude='build*' --exclude='.git' --exclude='.venv' --exclude='venv' --exclude='*.deb' --exclude='wheels' --exclude='sounds' --exclude='controllers' . build/opt/r2_control/

# Copy the existing service files to the system location
cp r2_control.service build/etc/systemd/system/
cp 99-r2-usb.rules build/etc/udev/rules.d/

# Final Build
dpkg-deb --build build "r2_control_lite_${CORE_VERSION}_${ARCH}.deb"

# ==========================================
# BUILD 2: OFFLINE PACKAGE (WHEELS BUNDLED)
# ==========================================
echo "Building Core Offline Package..."
# Swap the metadata to the offline postinst script
cp packaging/postinst.offline build/DEBIAN/postinst
chmod +x build/DEBIAN/postinst

# Generate Pre-Compiled Offline Wheels (Since you build in ARM via QEMU, this produces ARM binaries!)
mkdir -p build/opt/r2_control/wheels
python3 -m pip wheel -w build/opt/r2_control/wheels --pre pygame
python3 -m pip wheel -w build/opt/r2_control/wheels -r requirements.txt

# Final Build
dpkg-deb --build build "r2_control_offline_${CORE_VERSION}_${ARCH}.deb"

echo "Done!"