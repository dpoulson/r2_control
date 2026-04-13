#!/bin/bash
# packaging/start_test_vm.sh
# This script spins up a systemd-enabled ARM64 "Virtual Machine" (using Docker)
# so you can test installing and running the actual .deb package and systemd services.

echo "==============================================="
echo " Starting ARM64 Systemd Test Environment       "
echo "==============================================="

# Pull the base systemd debian image
docker pull --platform linux/arm64 jrei/systemd-debian:bookworm

# Stop previous instance if running
docker stop r2_test_vm 2>/dev/null
docker rm r2_test_vm 2>/dev/null

# Run the container in privileged mode so systemd can initialize fully
# Mapping port 8080 (apache) and 5000 (flask) to your localhost
docker run -d --name r2_test_vm \
    --privileged \
    --platform linux/arm64 \
    -p 8080:80 \
    -p 5000:5000 \
    -v /sys/fs/cgroup:/sys/fs/cgroup:ro \
    -v $(pwd):/mnt/r2_source \
    jrei/systemd-debian:bookworm

echo "Waiting for systemd to boot up inside the VM..."
sleep 5

echo "Installing prerequisites..."
docker exec r2_test_vm apt-get update
# Install utilities that might be needed by the package installer
docker exec r2_test_vm apt-get install -y python3 python3-pip python3-venv apache2 php sudo kmod iptables dbus

echo "==============================================="
echo " Environment is ready!"
echo " "
echo " To install the lite package and trigger your postinst systemctl scripts:"
echo " docker exec r2_test_vm dpkg -i /mnt/r2_source/r2_control_lite_1.0_arm64.deb"
echo " "
echo " To execute an interactive shell inside the VM, run:"
echo " docker exec -it r2_test_vm /bin/bash"
echo " "
echo " Remember to check http://localhost:8080 in your browser!"
echo " When you are done, run: docker rm -f r2_test_vm"
echo "==============================================="
