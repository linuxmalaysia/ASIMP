#!/usr/bin/env bash
# ==============================================================================
# ASIMP Unified Module Installation & Environment Bootstrap Script
# ==============================================================================
# Description: Automates virtual environment setup via Python uv, installs
#              required Python packages, and retrieves Ansible Galaxy dependencies.
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

echo "========================================================================"
echo "          ASIMP UNIFIED INSTALLATION & BOOTSTRAP SCRIPT"
echo "========================================================================"

# 1. Check for Python 3
if ! command -v python3 &>/dev/null; then
    echo "[!] Error: python3 is not installed or not in PATH." >&2
    exit 1
fi

echo "[*] Python 3 detected: $(python3 --version)"

# 2. Check for uv or prompt installation instructions
if ! command -v uv &>/dev/null; then
    echo "[*] Python 'uv' installer not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="${HOME}/.local/bin:${PATH}"
fi

echo "[*] Python 'uv' detected: $(uv --version)"

# 3. Create virtual environment if it does not exist
VENV_DIR="${REPO_ROOT}/.venv"
if [ ! -d "${VENV_DIR}" ]; then
    echo "[*] Creating virtual environment at .venv using uv..."
    uv venv "${VENV_DIR}"
fi

echo "[*] Activating virtual environment..."
source "${VENV_DIR}/bin/activate"

# 4. Install Python dependencies
if [ -f "${REPO_ROOT}/requirements.txt" ]; then
    echo "[*] Installing Python dependencies from requirements.txt..."
    uv pip install -r "${REPO_ROOT}/requirements.txt"
else
    echo "[!] Warning: requirements.txt not found." >&2
fi

# 5. Download Ansible Galaxy roles and collections
if command -v ansible-galaxy &>/dev/null && [ -f "${REPO_ROOT}/requirements.yml" ]; then
    echo "[*] Installing Ansible Galaxy dependencies from requirements.yml..."
    ansible-galaxy install -r "${REPO_ROOT}/requirements.yml" --ignore-errors
fi

echo "========================================================================"
echo "      ASIMP INSTALLATION COMPLETE SUCCESSFUL!"
echo "========================================================================"
echo "To activate your environment run:"
echo "  source .venv/bin/activate"
echo "========================================================================"
