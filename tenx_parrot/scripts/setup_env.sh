#!/bin/bash

# Get environment stage from argument or use default
ENV_STAGE=${1:-dev}

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Function to check if a command exists
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${YELLOW}$1 is not installed. Installing...${NC}"
        return 1
    fi
    return 0
}

# Function to install uv
install_uv() {
    if ! check_command uv; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
    fi
    echo -e "${GREEN}uv is already installed${NC}"
}

# Function to create and activate virtual environment
setup_venv() {
    VENV_DIR=".venv"
    PYTHON_VERSION="3.12"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "$VENV_DIR" ]; then
        echo -e "${YELLOW}Creating virtual environment with Python $PYTHON_VERSION...${NC}"
        uv venv $VENV_DIR --python $PYTHON_VERSION
    fi

    # Activate virtual environment
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source $VENV_DIR/bin/activate
}

# Function to install dependencies
install_dependencies() {
    echo -e "${GREEN}Installing dependencies...${NC}"
    
    # First install core dependencies
    echo "Installing core dependencies..."
    uv pip install -r requirements.txt || {
        echo -e "${RED}Failed to install core dependencies${NC}"
        exit 1
    }
    
    # Then install dev dependencies if in dev mode
    if [ "$ENV_STAGE" = "test" ]; then
        echo "Installing development dependencies..."
        uv pip install -r requirements-test.txt || {
            echo -e "${RED}Failed to install test dependencies${NC}"
            exit 1
        }
    fi
}

# Function to generate environment configuration
generate_env() {
    echo -e "${GREEN}Generating environment configuration...${NC}"
    python scripts/generate_env.py --stage $ENV_STAGE || {
        echo -e "${RED}Failed to generate environment configuration${NC}"
        exit 1
    }
}

# Main setup process
echo -e "${GREEN}Setting up environment...${NC}"

# Install uv if not present
install_uv

# Setup virtual environment
setup_venv

# Install dependencies
install_dependencies

# Generate environment configuration
generate_env

echo -e "${GREEN}Setup completed successfully!${NC}" 