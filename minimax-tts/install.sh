#!/bin/bash

# MiniMax TTS Voice Cloning Tool - Installation Script
# This script installs the required dependencies for the voice_cloner.py tool

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"
LAUNCHER="$SCRIPT_DIR/voice_cloner"

echo "=========================================="
echo "MiniMax TTS Voice Cloning Tool Installer"
echo "=========================================="
echo ""

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed."
    echo "Please install Python 3 first:"
    echo "  - macOS: brew install python3"
    echo "  - Ubuntu/Debian: sudo apt-get install python3"
    echo "  - Windows: Install Python from https://python.org"
    exit 1
fi

# Check if virtual environment already exists
if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists at $VENV_DIR"
    echo "Using existing virtual environment..."
else
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo "Virtual environment created at $VENV_DIR"
fi

# Create launcher script if it doesn't exist
if [ ! -f "$LAUNCHER" ]; then
    echo ""
    echo "Creating launcher script..."
    cat > "$LAUNCHER" << 'LAUNCHER_EOF'
#!/bin/bash

# MiniMax TTS Voice Cloning Tool - Launcher Script
# This script automatically uses the virtual environment's Python

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Virtual environment not found at $VENV_DIR"
    echo "Please run ./install.sh first"
    exit 1
fi

# Use Python from virtual environment
exec "$VENV_DIR/bin/python" "$SCRIPT_DIR/voice_cloner.py" "$@"
LAUNCHER_EOF
    chmod +x "$LAUNCHER"
    echo "Launcher script created at $LAUNCHER"
fi

# Upgrade pip in virtual environment
echo ""
echo "Upgrading pip..."
"$VENV_DIR/bin/pip" install --upgrade pip

echo ""
echo "Installing dependencies..."

# Install requests from requirements.txt
echo "Installing requests library..."
"$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"

echo ""
echo "=========================================="
echo "Installation completed successfully!"
echo "=========================================="
echo ""
echo "Run the voice cloner:"
echo "  ./voice_cloner --help"
echo ""
echo "Or activate virtual environment first:"
echo "  source venv/bin/activate"
echo "  ./voice_cloner.py --help"
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
echo "   ./voice_cloner --help"
echo ""
echo "For more information, see USAGE.md"
echo ""
