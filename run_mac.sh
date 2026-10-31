#!/usr/bin/env bash
# ==============================================================================
# BEOMCHRO (범크로) macOS Launcher
# NOL-TICKET ULTRA FAST QUEUE INTERCEPTOR v2.0
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=================================================================="
echo "⚡ BEOMCHRO HYBRID QUEUE INTERCEPTOR v2.0 (macOS)"
echo "=================================================================="

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ [ERROR] python3 is not installed or not in PATH."
    echo "   Please install Python 3.9+ using: brew install python"
    exit 1
fi

VENV_DIR="$SCRIPT_DIR/.venv"

# Create virtual environment if missing
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment (.venv)..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Install/Update requirements if needed
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    echo "🔄 Checking and installing dependencies..."
    pip install --upgrade pip --quiet
    pip install -r "$SCRIPT_DIR/requirements.txt" --quiet
fi

# Run BEOMCHRO Core
echo "🚀 Launching BEOMCHRO TUI Dashboard..."
python "$SCRIPT_DIR/beomchro_core.py" "$@"
