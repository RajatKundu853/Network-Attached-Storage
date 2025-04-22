#!/bin/bash

# Update package list
echo "[+] Updating package list..."
sudo apt update -y

# Install dependencies
echo "[+] Installing dependencies..."
sudo apt install -y curl

# Add Ngrok's GPG key
echo "[+] Adding Ngrok GPG key..."
curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null

# Add Ngrok's repository
echo "[+] Adding Ngrok repository..."
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list

# Update package list again
echo "[+] Updating package list again..."
sudo apt update -y

# Install Ngrok
echo "[+] Installing Ngrok..."
sudo apt install -y ngrok

echo "=============================="
echo "        Ngrok Setup"
echo "=============================="
echo ""
echo "Please follow the steps below to connect your Ngrok account:"
echo ""
echo "1. Visit the Ngrok website: https://dashboard.ngrok.com/get-started/your-authtoken"
echo "2. Sign up or log in to your Ngrok account."
echo "3. Copy your personal Auth Token from the dashboard."
echo "4. Paste the token below when prompted."
echo ""

# Ask user for Ngrok auth token
read -p "Enter your Ngrok Auth Token: " AUTH_TOKEN

# Configure Ngrok with the entered authentication token
echo "[+] Configuring Ngrok authentication..."
ngrok config add-authtoken "$AUTH_TOKEN"

echo "[✓] Ngrok has been authenticated successfully!"

echo "Please wait while we set things up..."
sleep 5
echo "[✓] Ngrok setup complete!"
# Start Ngrok on port 8000
echo "[+] Starting Ngrok on port 8000..."
sleep 4 

ngrok http 8000
