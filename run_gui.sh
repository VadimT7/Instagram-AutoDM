#!/bin/bash

echo "==============================================="
echo "Instagram DM Automation System - GUI"
echo "==============================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python from https://www.python.org/"
    exit 1
fi

# Run the GUI
python3 gui.py

