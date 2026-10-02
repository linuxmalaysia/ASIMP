#!/usr/bin/env bash
# ==============================================================================
# ASIMP Ansible Execution Environment (EE) Builder Script
# ==============================================================================
# Requirement:
#   - ansible-builder (v3+)
#   - podman or docker
#
# Usage:
#   ./scripts/build_ee.sh [TAG] [BUILD_CONTEXT_DIR]
#   Example: ./scripts/build_ee.sh asimp-ee:latest /tmp/asimp-ee-context
# ==============================================================================

set -euo pipefail

# Resolve execution-environment configuration directory relative to script
EE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../execution-environment" && pwd)"

# Define container image tag argument with default asimp-ee:latest
TAG="${1:-asimp-ee:latest}"

# Define temporary container build context output directory argument
BUILD_CONTEXT="${2:-/tmp/asimp-ee-context}"

echo "========================================================================"
echo " Building ASIMP Execution Environment: ${TAG}"
echo " Configuration Directory: ${EE_DIR}"
echo " Build Context: ${BUILD_CONTEXT}"
echo "========================================================================"

# Validate that ansible-builder CLI tool is available in environment PATH
if ! command -v ansible-builder &>/dev/null; then
    echo "[!] Error: 'ansible-builder' executable not found in current PATH." >&2
    echo "[!] Install via: pip install ansible-builder or uv pip install ansible-builder" >&2
    exit 1
fi

# Check for container runtime engine (Podman or Docker)
if ! command -v podman &>/dev/null && ! command -v docker &>/dev/null; then
    echo "[!] Warning: Container engine (podman or docker) not found in PATH."
fi

# Ensure output directory for container context exists
mkdir -p "${BUILD_CONTEXT}"

# Generate Containerfile and build context directory using ansible-builder v3 options
echo "[*] Creating container build context and Containerfile via ansible-builder..."
ansible-builder create \
    --file "${EE_DIR}/execution-environment.yml" \
    --context "${BUILD_CONTEXT}"

# Trigger container image build and tag using ansible-builder v3 options
echo "[*] Triggering container build for tag '${TAG}'..."
ansible-builder build \
    --file "${EE_DIR}/execution-environment.yml" \
    --tag "${TAG}" \
    --context "${BUILD_CONTEXT}"

echo "[+] Successfully built Ansible Execution Environment image: ${TAG}"
echo "========================================================================"
