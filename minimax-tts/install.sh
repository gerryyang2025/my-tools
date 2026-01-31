#!/bin/bash

# MiniMax TTS Voice Cloning Tool - Installation Script
# This script installs the required dependencies for the voice_cloner.py tool

set -e  # Exit on error

echo "=========================================="
echo "MiniMax TTS Voice Cloning Tool Installer"
echo "=========================================="
echo ""

# Check if pip is available
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "Error: pip is not installed."
    echo "Please install pip first:"
    echo "  - macOS: brew install python3"
    echo "  - Ubuntu/Debian: sudo apt-get install python3-pip"
    echo "  - Windows: Install Python from https://python.org"
    exit 1
fi

# Get pip command
PIP_CMD="pip3"
if ! command -v pip3 &> /dev/null; then
    PIP_CMD="pip"
fi

echo "Installing dependencies..."
echo ""

# Install requests
echo "Installing requests library..."
$PIP_CMD install -r requirements.txt

echo ""
echo "=========================================="
echo "Installation completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Configure your MiniMax API key:"
echo "   Option A: Set environment variable"
echo "     export MINIMAX_API_KEY='your-api-key'"
echo ""
echo "   Option B: Create .env file (recommended)"
echo "     cp .env.example .env"
echo "     # Then edit .env and fill in your API key"
echo ""
echo "2. Run the voice cloning tool:"
echo "   ./voice_cloner.py --help"
echo ""
echo "For more information, see USAGE.md"
echo ""
