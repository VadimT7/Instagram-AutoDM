#!/bin/bash

echo "========================================"
echo "Instagram Automation Pro - Modern UI"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8+ first"
    exit 1
fi

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    
    echo "Installing requirements..."
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# Launch the modern GUI
echo "Launching Modern UI..."
python gui_modern.py

deactivate
