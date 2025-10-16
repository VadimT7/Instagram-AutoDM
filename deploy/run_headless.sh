#!/bin/bash

###############################################################################
# Instagram Automation - Headless Runner Script
# Runs the automation in headless mode with virtual display
###############################################################################

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "Error: Virtual environment not found. Run setup_ubuntu.sh first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found. Please create it with your Instagram credentials."
    exit 1
fi

# Set up virtual display for headless operation (if needed)
export DISPLAY=:99
if ! pgrep Xvfb > /dev/null; then
    echo "Starting virtual display..."
    Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
    sleep 2
fi

# Run the automation
echo "Starting Instagram automation in headless mode..."
python main.py

# Exit with the same code as the Python script
exit $?

