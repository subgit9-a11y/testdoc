#!/bin/bash
# Script to add 8GB swap memory on Vultr instance
# This prevents OOM (Out of Memory) crashes when loading Llama and IndicTrans models.
echo "Setting up 8GB Swap Space to prevent OOM crashes..."

# Check if swapfile already exists
if swapon --show | grep -q "/swapfile"; then
    echo "Swap space already exists!"
    swapon --show
    exit 0
fi

# Allocate 8GB
fallocate -l 8G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# Persist across reboots
if ! grep -q "/swapfile" /etc/fstab; then
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

echo "Swap setup complete!"
swapon --show
