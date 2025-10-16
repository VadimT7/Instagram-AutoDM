#!/bin/bash

###############################################################################
# Instagram Automation - Ubuntu Server Setup Script
# This script sets up all dependencies for running the automation on Ubuntu
###############################################################################

set -e  # Exit on error

echo "========================================="
echo "Instagram Automation - Server Setup"
echo "========================================="
echo ""

# Update system packages
echo "[1/7] Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3.11+ and pip
echo "[2/7] Installing Python and pip..."
sudo apt-get install -y python3 python3-pip python3-venv

# Install Chrome browser
echo "[3/7] Installing Google Chrome..."
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
sudo apt-get update
sudo apt-get install -y google-chrome-stable

# Install ChromeDriver dependencies
echo "[4/7] Installing system dependencies..."
sudo apt-get install -y \
    xvfb \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    wget \
    unzip

# Create virtual environment
echo "[5/7] Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "[6/7] Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "[7/7] Creating directories..."
mkdir -p session_data
mkdir -p logs

# Set permissions
chmod +x deploy/run_headless.sh

echo ""
echo "========================================="
echo "Setup completed successfully!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Create/upload your .env file with Instagram credentials"
echo "2. Update InstagramProfiles.csv with target usernames"
echo "3. Test run: source venv/bin/activate && python main.py"
echo "4. Set up systemd service: sudo cp deploy/instagram-automation.service /etc/systemd/system/"
echo ""

