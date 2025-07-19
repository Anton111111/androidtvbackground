#!/bin/bash

# Check if a script name was provided
if [ -z "$1" ]; then
    echo "Usage: $0 <script_name.py> [script arguments...]"
    exit 1
fi

# First CLI argument is the Python script to run
SCRIPT_NAME="$1"
shift                     # Shift so that "$@" now holds arguments for the Python script

# Directory where the virtual environment will live
VENV_DIR="venv"

# Verify the target Python script exists
if [ ! -f "$SCRIPT_NAME" ]; then
    echo "Error: Script '$SCRIPT_NAME' not found."
    exit 1
fi

# Create the virtual environment if it doesn’t already exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate the virtual environment
source "$VENV_DIR/bin/activate"

# Install dependencies if a requirements.txt file is present
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
fi

# Run the Python script with any additional arguments the user supplied
echo "Running $SCRIPT_NAME..."
python "$SCRIPT_NAME" "$@"

# Deactivate the virtual environment (optional)
deactivate
