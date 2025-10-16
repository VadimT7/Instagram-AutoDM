#!/bin/bash

echo "==============================================="
echo "Instagram DM Automation System"
echo "==============================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python from https://www.python.org/"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created."
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update requirements
echo "Checking dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    if [ -f "env.example" ]; then
        echo "Warning: .env file not found!"
        echo "Please copy env.example to .env and add your Instagram credentials"
        echo ""
        read -p "Press Enter to continue..."
    fi
fi

# Run the main script
echo "Starting Instagram DM Automation..."
echo ""
python3 main.py

# Deactivate virtual environment
deactivate

echo ""
echo "==============================================="
echo "Automation completed."
echo "==============================================="
