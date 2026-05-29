#!/usr/bin/env bash

# Exit on error
set -e

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install uv if not present
install_uv() {
    if ! command_exists uv; then
        echo "Installing uv package manager..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
    fi
}

# Function to create virtual environment
create_venv() {
    if [ ! -d ".venv" ]; then
        echo "Creating virtual environment..."
        python -m venv .venv
    fi
}

# Function to activate virtual environment
activate_venv() {
    echo "Activating virtual environment..."
    source .venv/bin/activate
}

# Function to install dependencies
install_deps() {
    echo "Installing dependencies..."
    uv pip install -r requirements.txt
    uv pip install -r requirements-dev.txt
}

# Function to run tests
run_tests() {
    echo "Running tests..."
    pytest -v --cov=tenx_ipersona tests/
}

# Main script
echo "Setting up test environment..."

# Install uv if not present
install_uv

# Create and activate virtual environment if it doesn't exist
create_venv
activate_venv

# Install dependencies
install_deps

# Run tests
run_tests

echo "Test environment setup and tests completed successfully!" 