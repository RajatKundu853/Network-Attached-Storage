#!/bin/bash

if ! command -v figlet &> /dev/null; then
    echo "[+] Installing figlet..."
    sudo apt install -y figlet
fi

if ! command -v toilet &> /dev/null; then
    echo "[+] Installing toilet..."
    sudo apt install -y toilet
fi

# Generate stylish font for "NAShield" and "author: Rajat Kundu"
clear

figlet -f slant "NAShield"
echo
toilet -f term -F border "Author: Rajat Kundu"
echo

echo "╭───────────────────────────────────────────────╮"
echo "│      📦 Installing all dependencies...        │"
echo "│    ⚙️  Setting up a comfortable environment    │"
echo "│         for your NAS to run smoothly.         │"
echo "╰───────────────────────────────────────────────╯"


# List of required dependencies
DEPENDENCIES=(
    "python3"
    "python3-pip"
    "git"
    "curl"
    "gcc"
    "make"
    "libpcap-dev"
    "build-essential"
    "libssl-dev"
    "python3-dev"
   
)

# Update the system's package list
echo "Updating package list..."
sudo apt update

# Check for each dependency and install if not present
for DEP in "${DEPENDENCIES[@]}"; do
    if dpkg -l | grep -q "^ii  $DEP"; then
        echo "$DEP is already installed."
    else
        echo "$DEP is not installed. Installing..."
        sudo apt install -y $DEP
    fi
done

# Check for Python packages (using pip)
PIP_DEPENDENCIES=(
    "requests"
    "flask"
    "pillow"
    "pyserial"
    "scapy"
    "numpy"
)

# Check and install pip packages
for PIP in "${PIP_DEPENDENCIES[@]}"; do
    if python3 -m pip show $PIP &>/dev/null; then
        echo "$PIP Python package is already installed."
    else
        echo "$PIP Python package is not installed. Installing..."
        python3 -m pip install --upgrade pip
        python3 -m pip install $PIP
    fi
done

echo "All dependencies are checked and installed successfully!"


sleep 5
echo "Just set up your environment..."
clear
bash 1.sh

sleep 2

echo "[✔] All set! Your NAS environment is ready."
sleep 2
echo "Please wait your NAS is starting..."

clear
echo "Starting NAS services..."
figlet -f slant "NAShield"
echo
toilet -f term -F border "Author: Rajat Kundu"
echo
python3 2.py 


