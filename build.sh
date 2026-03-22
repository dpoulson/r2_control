# 1. Create the structure for the .deb inside a temporary folder
mkdir -p build/DEBIAN
mkdir -p build/opt/r2_control
mkdir -p build/etc/systemd/system
mkdir -p build/etc/apache2/sites-available

# 2. Copy metadata from your new 'packaging' folder
cp packaging/postinst build/DEBIAN/
cp packaging/prerm build/DEBIAN/
chmod +x build/DEBIAN/postinst build/DEBIAN/prerm

# 3. Use sed to create the real control file from your template
# This allows us to inject the version and architecture dynamically
sed "s/{{VERSION}}/1.0/g; s/{{ARCHITECTURE}}/arm64/g" packaging/control.template > build/DEBIAN/control

# 4. Copy your existing code into the /opt/ location
# We exclude the 'build' and '.git' folders to keep the package small
rsync -av --exclude='build' --exclude='.git' --exclude='*.deb' . build/opt/r2_control/

# 5. Copy the existing service file to the system location
cp r2_control.service build/etc/systemd/system/

cp controllers/www/apache.conf build/etc/apache2/sites-available/000-r2.conf

# 6. Build the venv inside the build folder (native ARM via QEMU)
python3 -m venv build/opt/r2_control/venv
# Upgrade pip first to ensure it handles modern wheels
build/opt/r2_control/venv/bin/python3 -m pip install --upgrade pip

# Install pygame pre-release specifically
build/opt/r2_control/venv/bin/python3 -m pip install pygame --pre
build/opt/r2_control/venv/bin/pip install -r requirements.txt

# 7. Final Build
dpkg-deb --build build r2_control_1.0_arm64.deb