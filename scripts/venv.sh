#!/bin/bash

# Directory where the virtual environment will be created
VENV_DIR="venv"

# Check if a directory argument is provided
if [ ! -z "$1" ]; then
  VENV_DIR=$1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "Python3 could not be found. Please install Python3."
    exit 1
fi

# Create a virtual environment
echo "Creating virtual environment in directory: $VENV_DIR"
python3 -m venv $VENV_DIR

# Check if the virtual environment was created successfully
if [ ! -d "$VENV_DIR" ]; then
  echo "Failed to create virtual environment."
  exit 1
fi

# Activate the virtual environment
source $VENV_DIR/bin/activate

# Check if the virtual environment was activated successfully
if [ "$VIRTUAL_ENV" != "" ]; then
  echo "Virtual environment activated successfully."
else
  echo "Failed to activate virtual environment."
  exit 1
fi

echo "Virtual environment setup complete. To deactivate, run 'deactivate'."

