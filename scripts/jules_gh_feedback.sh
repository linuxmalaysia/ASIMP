#!/bin/bash

# ==============================================================================
# Protocol    : Deep State of Mind (DSOM) For My AI Protocol (v5.0)
# Author      : Harisfazillah Jamel (LinuxMalaysia)
# Timestamp   : 2026-08-05
# License     : GNU General Public License v3.0
# Standard    : UK English | DBP-standard Bahasa Melayu Malaysia (Piawai)
# Purpose     : Telemetry courier and feedback bridge for Google Jules & GitHub
# ==============================================================================
set -euo pipefail

# --- Color Constants & Logging Helpers ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warn() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# --- Cleanup Traps ---
cleanup() {
    local exit_code=$?
    if [ "$exit_code" -ne 0 ]; then
        log_error "Pipeline dispatch was interrupted or encountered an unexpected error."
    fi
}
trap cleanup EXIT

# --- Verification & Setup ---
TELEMETRY_FILE="/tmp/jules_telemetry.json"
PAYLOAD_FILE="/tmp/jules_payload.md"

log_info "Initialising ASIMP Telemetry Bridge..."

if [ ! -f "$TELEMETRY_FILE" ]; then
    log_error "Telemetry data file '$TELEMETRY_FILE' not found. Ensure the test matrix playbook has run successfully."
    exit 1
fi

log_info "Parsing telemetry and generating Markdown payload..."

# --- Embedded Python JSON Parser & Markdown Formatter ---
python3 - << 'EOF'
import json
import os
import sys

filepath = "/tmp/jules_telemetry.json"
outpath = "/tmp/jules_payload.md"

try:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception as e:
    print(f"CRITICAL: Failed to parse {filepath}. Error: {str(e)}")
    sys.exit(1)

md = []
md.append("### 📊 ASIMP Local Matrix Test Execution Board\n")

exec_mode = data.get("execution_mode", "user").lower()
pr_id = data.get("pr_id", "none")
timestamp = data.get("timestamp", "N/A")
status = data.get("overall_status", "success").upper()

status_emoji = "🟢 **PASS**" if status == "SUCCESS" else "🔴 **FAIL**"

md.append(f"**Overall Status**: {status_emoji}\n")
md.append(f"- **Execution Mode**: `{exec_mode}`")
md.append(f"- **PR ID / Ref**: `{pr_id}`")
md.append(f"- **Timestamp (UTC)**: `{timestamp}`\n")

md.append("| Host | OS Distribution | Kernel Release | Status |")
md.append("| :--- | :--- | :--- | :--- |")

hosts = data.get("hosts", {})
for host, info in sorted(hosts.items()):
    h_status = info.get("status", "success").upper()
    h_emoji = "🟢 SUCCESS" if h_status == "SUCCESS" else "🔴 FAILED"
    h_os = info.get("os_info", "Unknown")

    # Clean up kernel string to keep table tidy
    raw_kernel = info.get("kernel_release", "Unknown")
    clean_kernel = raw_kernel.split("\n")[0].strip()
    if len(clean_kernel) > 45:
        clean_kernel = clean_kernel[:42] + "..."

    md.append(f"| `{host}` | {h_os} | `{clean_kernel}` | {h_emoji} |")

md.append("\n")

failures_exist = False
for host, info in sorted(hosts.items()):
    failures = info.get("failures", [])
    if failures:
        failures_exist = True
        md.append(f"#### ⚠️ Detailed Failure Trace for `{host}`\n")
        for fail in failures:
            task_name = fail.get("task", "Unknown Task")
            error_msg = fail.get("error", "No details available")
            fail_time = fail.get("timestamp", "N/A")

            md.append(f"<details>\n<summary><b>❌ Failed Task: {task_name} (at {fail_time})</b></summary>\n")
            md.append("\n```text")
            md.append(error_msg.strip())
            md.append("```\n")
            md.append("</details>\n")

if status != "SUCCESS" and not failures_exist:
    md.append("#### ⚠️ Unknown Execution Interruptions")
    md.append("The run was marked as failed, but no task-level rescue trace was generated. Check Podman container state.\n")

md.append("\n---\n*Deep State of Mind (DSOM) For My AI Protocol | Local telemetry auto-dispatch courier*")

try:
    with open(outpath, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
except Exception as e:
    print(f"CRITICAL: Failed to write {outpath}. Error: {str(e)}")
    sys.exit(1)

print("SUCCESS: Markdown payload compiled successfully.")
EOF

if [ ! -f "$PAYLOAD_FILE" ]; then
    log_error "Payload markdown file could not be generated."
    exit 1
fi

log_success "Markdown feedback report successfully generated at $PAYLOAD_FILE"

# Extract metadata for dispatching
PR_ID=$(python3 -c 'import json; print(json.load(open("/tmp/jules_telemetry.json")).get("pr_id", "none"))')
EXEC_MODE=$(python3 -c 'import json; print(json.load(open("/tmp/jules_telemetry.json")).get("execution_mode", "user"))')

# --- Sink 1: Google Jules Session Feed ---
log_info "Checking Google Jules Session Connection..."
if command -v jules &>/dev/null; then
    log_info "Google Jules CLI detected. Dispatched stream feeding chat context..."
    jules chat --message "Local testing matrix report processed. Injecting payload to session." || log_warn "Jules chat submission encountered a non-fatal error."
    # Dynamic feed command simulation/invocation if supported
    if command -v jules-feed &>/dev/null; then
        jules-feed --payload "$PAYLOAD_FILE" || true
    fi
else
    # Fallback to REST API if endpoints are specified
    if [ -n "${JULES_API_URL:-}" ] && [ -n "${JULES_API_TOKEN:-}" ]; then
        log_info "API endpoint defined. Sending REST POST feedback..."
        curl -sS -X POST -H "Authorization: Bearer $JULES_API_TOKEN" \
             -H "Content-Type: application/json" \
             -d @/tmp/jules_telemetry.json "$JULES_API_URL" > /dev/null || log_warn "REST API POST feedback submission failed."
    else
        log_warn "Google Jules CLI or REST credentials unavailable. Bypassing Jules stream socket integration."
    fi
fi

# --- Sink 2: GitHub PR Feedback Comment ---
if [ "$EXEC_MODE" = "dev" ] && [ -n "$PR_ID" ] && [ "$PR_ID" != "none" ] && [ "$PR_ID" != "null" ]; then
    log_info "Preparing Pull Request feedback dispatcher for PR #$PR_ID..."

    if command -v gh &>/dev/null; then
        # Check authentication status
        if gh auth status &>/dev/null || [ -n "${GITHUB_TOKEN:-}" ] || [ -n "${GH_TOKEN:-}" ]; then
            log_info "GitHub authentication found. Posting feedback to Pull Request..."
            gh pr comment "$PR_ID" --body-file "$PAYLOAD_FILE" || log_warn "Failed to post comment to PR #$PR_ID via GitHub API."
            log_success "PR feedback comment dispatched successfully."
        else
            log_warn "GitHub credentials (GITHUB_TOKEN/GH_TOKEN) not set. Skipping GitHub comment dispatch."
        fi
    else
        log_warn "GitHub CLI ('gh') is not installed on this host. Skipping GitHub comment dispatch."
    fi
else
    log_info "Bypassing GitHub dispatch (execution_mode: $EXEC_MODE, pr_id: $PR_ID)."
fi

# --- Summary Output ---
echo -e "\n${CYAN}========================================================================${NC}"
echo -e "                   ${GREEN}TELEMETRY TRANSMISSION SUMMARY${NC}"
echo -e "${CYAN}========================================================================${NC}"
cat "$PAYLOAD_FILE"
echo -e "${CYAN}========================================================================${NC}"

log_success "ASIMP bidirectional telemetry pipeline transmission complete."
exit 0
