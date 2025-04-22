#!/bin/bash

# Define NAS directory
NAS_DIR="./NAS"

# Check if NAS directory exists, if not create it
if [ ! -d "$NAS_DIR" ]; then
    mkdir -p "$NAS_DIR"
    echo "NAS directory created at: $NAS_DIR"
else
    echo "NAS directory already exists at: $NAS_DIR"
fi

# List available partitions
echo "Available external storage partitions:"
lsblk -o NAME,MOUNTPOINT,SIZE,TYPE | grep "part"

# Prompt user to select partitions (space-separated)
read -p "Enter partition names to mount (e.g., sdb1 sdc1 sdd1): " PARTITIONS

# Loop through each partition entered
for PARTITION_NAME in $PARTITIONS; do
    DEVICE_PATH="/dev/$PARTITION_NAME"
    MOUNT_POINT="$NAS_DIR/$PARTITION_NAME"

    # Check if the partition exists
    if [ ! -e "$DEVICE_PATH" ]; then
        echo "Error: Partition $DEVICE_PATH not found! Skipping..."
        continue
    fi

    # Create a separate mount directory for each partition
    mkdir -p "$MOUNT_POINT"

    # Mount the partition to its respective directory
    sudo mount -o uid=1000,gid=1000,utf8 "$DEVICE_PATH" "$MOUNT_POINT"

    # Verify if mount was successful
    if mount | grep -q "$MOUNT_POINT"; then
        echo "Device $DEVICE_PATH successfully mounted to $MOUNT_POINT"
    else
        echo "Error mounting device $DEVICE_PATH. Check dmesg for more details."
    fi
done

# Display mounted partitions under NAS_DIR
echo "Mounted partitions:"
lsblk -o NAME,MOUNTPOINT | grep "$NAS_DIR"
