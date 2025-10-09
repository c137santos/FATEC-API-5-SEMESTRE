#!/bin/bash

echo "Setting up pre-commit hooks..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "Error: Not in a git repository root directory."
    echo "Please run this script from the root of the git repository."
    exit 1
fi

# Set up a dedicated virtual environment for pre-commit
echo "Setting up a dedicated virtual environment for pre-commit..."

# Create a virtual environment if it doesn't exist
if [ ! -d ".pre-commit-venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .pre-commit-venv
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment."
        echo "Make sure python3-venv is installed:"
        echo "sudo apt install python3-venv"
        exit 1
    fi
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source .pre-commit-venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment."
    exit 1
fi

# Install pre-commit and gitlint
echo "Installing pre-commit and gitlint..."
pip install --upgrade pip
pip install pre-commit gitlint
if [ $? -ne 0 ]; then
    echo "Failed to install pre-commit and gitlint."
    exit 1
fi

# Add pre-commit and gitlint to requirements-dev.txt if not already there
if ! grep -q "pre-commit" requirements-dev.txt; then
    echo "Adding pre-commit to requirements-dev.txt"
    echo "pre-commit>=3.0.0" >> requirements-dev.txt
fi

if ! grep -q "gitlint" requirements-dev.txt; then
    echo "Adding gitlint to requirements-dev.txt"
    echo "gitlint>=0.19.0" >> requirements-dev.txt
fi

# Install the git hooks
echo "Installing git hooks..."
pre-commit uninstall || true
pre-commit install --install-hooks
if [ $? -ne 0 ]; then
    echo "Failed to install pre-commit hooks."
    exit 1
fi

echo "Installing commit-msg hook for gitlint..."
pre-commit install --hook-type commit-msg --install-hooks
if [ $? -ne 0 ]; then
    echo "Failed to install commit-msg hooks."
    exit 1
fi

# verify the hooks
echo "Verifying hooks installation..."
if [ -f ".git/hooks/pre-commit" ] && [ -f ".git/hooks/commit-msg" ]; then
    echo "Pre-commit hooks installed successfully!"
else
    echo "WARNING: Hooks files not found in .git/hooks/"
    echo "Please check your git configuration and try again."
    exit 1
fi
