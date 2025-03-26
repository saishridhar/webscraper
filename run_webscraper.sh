#!/bin/bash

# Exit on error
set -e

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if script was called with --setup-only flag
SETUP_ONLY=false
for arg in "$@"; do
    if [ "$arg" == "--setup-only" ]; then
        SETUP_ONLY=true
        echo "Running in setup-only mode - will create venv and install deps but not start webscraper"
        break
    fi
done

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if UV is installed
if ! command_exists uv; then
    echo "Error: UV is not installed. Please install UV first:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Determine the virtual environment path based on OS
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    VENV_PATH="$SCRIPT_DIR/.venv/Scripts/activate"
else
    VENV_PATH="$SCRIPT_DIR/.venv/bin/activate"
fi

# Check if virtual environment exists
if [[ ! -f "$VENV_PATH" ]]; then
    echo "Creating virtual environment..."
    uv venv
    if [[ ! -f "$VENV_PATH" ]]; then
        echo "Error: Failed to create virtual environment"
        exit 1
    fi
    echo "Virtual environment created successfully"
fi

# Check if webscraper.py exists
if [[ ! -f "$SCRIPT_DIR/webscraper.py" ]]; then
    echo "Error: webscraper.py not found in $SCRIPT_DIR"
    exit 1
fi

# Check if requirements.txt exists
if [[ ! -f "$SCRIPT_DIR/requirements.txt" ]]; then
    echo "Error: requirements.txt not found in $SCRIPT_DIR"
    exit 1
fi

# Check if virtual environment is activated
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo "Activating virtual environment..."
    source "$VENV_PATH"
    
    # Verify activation was successful
    if [[ -z "${VIRTUAL_ENV}" ]]; then
        echo "Error: Failed to activate virtual environment"
        exit 1
    fi
    echo "Virtual environment activated successfully"
fi

# Clean any existing pip cache
echo "Cleaning pip cache..."
uv cache clean pip > /dev/null 2>&1

# Ensure dependencies are installed
echo "Installing dependencies (output redirected)..."
# Redirect stdout and stderr of uv pip install to /dev/null
if ! uv pip install --requirement "$SCRIPT_DIR/requirements.txt" > /dev/null 2>&1; then
    echo "Error: Failed to install dependencies. Check logs or run manually for details."
    # Optionally run verbosely to a log file for debugging if needed
    # uv pip install -v --requirement "$SCRIPT_DIR/requirements.txt" > install.log 2>&1
    exit 1
fi
# Diagnostic print moved *after* install confirmation
echo "Dependencies installed successfully."

# Exit here if --setup-only was specified
if $SETUP_ONLY; then
    echo "Setup completed successfully. Exiting without starting webscraper."
    exit 0
fi

# Add this line for diagnostics
echo "[run_webscraper.sh] Attempting to start webscraper.py directly with python..."

echo "Starting webscraper..." # Optional line

# Run the webscraper DIRECTLY using the activated environment's python
python "$SCRIPT_DIR/webscraper.py"