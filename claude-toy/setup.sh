#!/usr/bin/env bash
# Install dependencies for claude-toy. Run from repo root or from claude-toy/.
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

_run_pip() {
    if command -v pip &>/dev/null; then
        pip install -r requirements.txt
    elif command -v pip3 &>/dev/null; then
        pip3 install -r requirements.txt
    else
        python3 -m pip install -r requirements.txt
    fi
}

echo "Installing claude-toy dependencies from $SCRIPT_DIR ..."
_run_pip

if [[ ! -f openai_config.json ]]; then
    echo ""
    echo "openai_config.json not found. Copying from openai_config.sample.json"
    echo "Edit openai_config.json: set provider (openai|anthropic), api_key, base_url, model — then run ./claude-toy"
    cp openai_config.sample.json openai_config.json
else
    echo "openai_config.json already exists, leaving it unchanged."
fi

echo ""
echo "Done. Run:  ./claude-toy"
