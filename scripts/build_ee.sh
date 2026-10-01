#!/usr/bin/env bash
# ==============================================================================
# ASIMP Ansible Execution Environment (EE) Builder Script
# ==============================================================================
# Automates building standardized Ansible Execution Environments using
# ansible-builder and Python uv acceleration for air-gapped carrier and
# enterprise bastion deployments.
# ==============================================================================

set -euo pipefail

EE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../execution-environment" && pwd)"
TAG="${1:-asimp-ee:latest}"
BUILD_CONTEXT="${2:-/tmp/asimp-ee-context}"

echo "========================================================================"
echo " Building ASIMP Execution Environment: ${TAG}"
echo " Configuration Directory: ${EE_DIR}"
echo " Build Context: ${BUILD_CONTEXT}"
echo "========================================================================"

if ! command -v ansible-builder &>/dev/null; then
    echo "[!] Error: 'ansible-builder' executable not found in current PATH." >&2
    echo "[!] Install via: pip install ansible-builder or uv pip install ansible-builder" >&2
    exit 1
fi

if ! command -v podman &>/dev/null && ! command -v docker &>/dev/null; then
    echo "[!] Warning: Container engine (podman or docker) not found in PATH."
fi

mkdir -p "${BUILD_CONTEXT}"

echo "[*] Creating container build context and Containerfile via ansible-builder..."
ansible-builder create \
    --filename "${EE_DIR}/execution-environment.yml" \
    --output-filename Containerfile \
    --output-dir "${BUILD_CONTEXT}"

echo "[*] Triggering container build for tag '${TAG}'..."
ansible-builder build \
    --filename "${EE_DIR}/execution-environment.yml" \
    --tag "${TAG}" \
    --output-dir "${BUILD_CONTEXT}"

echo "[+] Successfully built Ansible Execution Environment image: ${TAG}"
echo "========================================================================"
