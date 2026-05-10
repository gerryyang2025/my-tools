#!/bin/bash

# MiniMax TTS Voice Cloning Tool - Installation Script
# Creates the virtualenv, installs dependencies, initializes local config, and verifies the setup.

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
LEGACY_VENV="$SCRIPT_DIR/venv"
LAUNCHER="$SCRIPT_DIR/voice_cloner"
ENV_FILE="$SCRIPT_DIR/.env"
ENV_EXAMPLE="$SCRIPT_DIR/.env.example"

echo "=========================================="
echo "MiniMax TTS Voice Cloning Tool Installer"
echo "=========================================="
echo ""

# --- Prerequisites ---
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed."
    echo "Please install Python 3 first:"
    echo "  - macOS: brew install python3"
    echo "  - Ubuntu/Debian: sudo apt-get install python3"
    echo "  - Windows: Install Python from https://python.org"
    exit 1
fi

# --- Virtual environment (standard name: .venv) ---
if [ -d "$LEGACY_VENV" ] && [ ! -d "$VENV_DIR" ]; then
    echo "Renaming legacy venv/ -> .venv/"
    mv "$LEGACY_VENV" "$VENV_DIR"
elif [ -d "$LEGACY_VENV" ] && [ -d "$VENV_DIR" ]; then
    echo "Note: both venv/ and .venv/ exist — using .venv/ for installs."
    echo "      You can delete the unused venv/ after confirming ./voice_cloner works."
    echo ""
fi

if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists at $VENV_DIR"
    echo "Using existing virtual environment..."
else
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo "Virtual environment created at $VENV_DIR"
fi

ensure_venv_python_symlink() {
    if [ -x "$VENV_DIR/bin/python3" ] && [ ! -e "$VENV_DIR/bin/python" ]; then
        ln -sf python3 "$VENV_DIR/bin/python"
    fi
}
ensure_venv_python_symlink

# --- Launcher (always executable; create if missing) ---
if [ ! -f "$LAUNCHER" ]; then
    echo ""
    echo "Creating launcher script..."
    cat > "$LAUNCHER" << 'LAUNCHER_EOF'
#!/bin/bash

# MiniMax TTS Voice Cloning Tool - Launcher Script
# This script automatically uses the virtual environment's Python

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Virtual environment not found at $VENV_DIR"
    echo "Please run ./install.sh first"
    exit 1
fi

# Prefer python, fall back to python3 (some venvs only ship python3)
PYTHON_EXE="$VENV_DIR/bin/python"
[ -x "$PYTHON_EXE" ] || PYTHON_EXE="$VENV_DIR/bin/python3"
exec "$PYTHON_EXE" "$SCRIPT_DIR/scripts/voice_cloner.py" "$@"
LAUNCHER_EOF
    echo "Launcher script created at $LAUNCHER"
fi
chmod +x "$LAUNCHER"

# --- Local env file (API key placeholder) ---
echo ""
if [ -f "$ENV_FILE" ]; then
    echo "Config: .env already exists — left unchanged."
elif [ -f "$ENV_EXAMPLE" ]; then
    cp "$ENV_EXAMPLE" "$ENV_FILE"
    echo "Config: created .env from .env.example — edit .env and set MINIMAX_API_KEY."
else
    echo "Config: .env.example not found; create .env manually if you use file-based API config."
fi

# --- Python packages ---
echo ""
echo "Upgrading pip..."
"$VENV_DIR/bin/pip" install --upgrade pip

echo ""
echo "Installing dependencies from requirements.txt..."
"$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"

ensure_venv_python_symlink

# --- Verify ---
echo ""
echo "Verifying Python environment..."
_VPY="$VENV_DIR/bin/python"
[ -x "$_VPY" ] || _VPY="$VENV_DIR/bin/python3"
# Suppress urllib3+LibreSSL noise on macOS default Python (HTTPS still works; see urllib3#3020)
PYTHONWARNINGS=ignore "$_VPY" -c "import requests; print('  OK: requests', requests.__version__)"

echo ""
echo "=========================================="
echo "Installation completed successfully!"
echo "=========================================="
echo ""
echo "Run the tool (no need to activate the venv):"
echo "  ./voice_cloner --help"
echo ""
echo "macOS often has no global \`python\` command — only \`python3\`."
echo "After installing, use ONE of:"
echo "  1) Activate this venv, then \`python\` works:"
echo "     cd \"$SCRIPT_DIR\" && source .venv/bin/activate && hash -r"
echo "  2) Without activating (recommended if you see \"command not found: python\"):"
echo "     ./voice_cloner ..."
echo "     .venv/bin/python3 scripts/voice_cloner.py ..."
echo ""
echo "Next steps:"
echo "1. Configure your MiniMax API key (if not done):"
echo "   - Edit .env and set MINIMAX_API_KEY, or"
echo "   - export MINIMAX_API_KEY='your-api-key'"
echo ""
echo "2. Run the voice cloning tool:"
echo "   ./voice_cloner --help"
echo ""
echo "For more information, see USAGE.md"
echo ""
