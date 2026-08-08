#!/usr/bin/env python3
"""
Sitemap URL and Link Integrity Verification Script
Parses the generated sitemap.txt and sitemap.xml and ensures that:
1. Root sitemaps and deployed (docs/) sitemaps match perfectly.
2. All URLs are fully qualified and correctly structured.
3. Every GitBook URL (loaded from a separate validation inventory) exists and returns HTTP 200.
4. Every GitHub Pages URL exists on the live site (returns HTTP 200) OR matches an on-disk markdown source file in the docs/ folder (pre-merge validation).
"""

import os
import sys
import xml.etree.ElementTree as ET
import urllib.request
import urllib.error
import random
from urllib.parse import urlparse

# Strict set of allowed hostnames to prevent SSRF and arbitrary redirection (satisfies CodeQL requirements)
ALLOWED_HOSTS = {
    "linuxmalaysia.github.io",
    "malaysia-open-source-community.gitbook.io"
}

# Separate validation inventory for GitBook URLs
GITBOOK_URLS = [
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/1.-sovereign-governance/ai-initialization-sequence.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/1.-sovereign-governance/ai-master-protocol.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/1.-sovereign-governance/automation-audit-list.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/1.-sovereign-governance/byte-capped-execution-framework.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/1.-sovereign-governance/crisp2-operational-strategy.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/1.-sovereign-governance/digital-sovereignty-model.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/1.-sovereign-governance/dsom-automated-state-sync.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/1.-sovereign-governance/dsom-efficiency-protocols.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/1.-sovereign-governance/dsom-ingestion-latency-architecture.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/1.-sovereign-governance/dsom-mcp-architecture.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/1.-sovereign-governance/dsom-token-efficiency-report.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/1.-sovereign-governance/dsom-token-performance-playbook.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/1.-sovereign-governance/dsom-tri-phasic-cognitive-architecture.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/1.-sovereign-governance/github-actions-security-scanning.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/1.-sovereign-governance/gitops-aiops-ansible-strategy.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/1.-sovereign-governance/hub-and-spoke-model.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/1.-sovereign-governance/itil-alignment.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/1.-sovereign-governance/llm-wiki-adoption.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/1.-sovereign-governance/noss-integration-guide.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/1.-sovereign-governance/operational-guide.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/1.-sovereign-governance/operational-sovereignty.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/1.-sovereign-governance/python-uv-environment-guide.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/1.-sovereign-governance/sop-knowledge-first-discovery.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/1.-sovereign-governance/zero-global-memory.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/2.-operational-rituals/digital-sovereignty-operational-model-palace.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/2.-operational-rituals/eod-ritual.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/2.-operational-rituals/personalization.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/2.-operational-rituals/ritual-of-transition.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/2.-operational-rituals/sod-ritual.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/4.-ai-and-agent-protocols/ai-agent-skills-guide.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/4.-ai-and-agent-protocols/ai-cognitive-logging-protocol.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/4.-ai-and-agent-protocols/ai-cognitive-twin-protocol.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/4.-ai-and-agent-protocols/ai-response-template.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/4.-ai-and-agent-protocols/dsom-episodic-record-template.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/4.-ai-and-agent-protocols/howto-adopt-dsom.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/4.-ai-and-agent-protocols/howto-dsom-baseline.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/4.-ai-and-agent-protocols/howto-upgrade-dsom.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/4.-ai-and-agent-protocols/human-handover-context.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/4.-ai-and-agent-protocols/mirror-of-knowledge.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/4.-ai-and-agent-protocols/multi-agent-protocols.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/4.-ai-and-agent-protocols/reanimation-prompt-template.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/6.-ansible-and-infrastructure-automation/howto-setup-ansible-baseline.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/6.-ansible-and-infrastructure-automation/howto-setup-wsl-almalinux10.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/8.-ai-agent-skills-and-workflows/skill-1.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/8.-ai-agent-skills-and-workflows/skill-10.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/8.-ai-agent-skills-and-workflows/skill-11.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/8.-ai-agent-skills-and-workflows/skill-12.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/8.-ai-agent-skills-and-workflows/skill-2.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/8.-ai-agent-skills-and-workflows/skill-3.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/8.-ai-agent-skills-and-workflows/skill-4.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/8.-ai-agent-skills-and-workflows/skill-5.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/8.-ai-agent-skills-and-workflows/skill-6.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/8.-ai-agent-skills-and-workflows/skill-7.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/8.-ai-agent-skills-and-workflows/skill-8.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/8.-ai-agent-skills-and-workflows/skill-9.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/8.-ai-agent-skills-and-workflows/skill.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/8.-ai-agent-skills-and-workflows/subagent-orchestration-workflow.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/9.-references-and-genesis-papers/howto-bootstrap-sovereign-ai-project.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/9.-references-and-genesis-papers/okf-adoption-guide.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/9.-references-and-genesis-papers/the-sovereign-ai-agent-workspace-v2_-architecting-persistent-memory-custom-skills-and-contextual-con.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/agent-configurations/autonomous_agent_manifest.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/agent-configurations/copilot_instructions_template.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/agent-configurations/cursorrules_template.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/agent-configurations/sovereign-persona-template.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/agent-configurations/windsurfrules_template.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/dsom-automation-encyclopedia-docs-tools/howto-audit-pre-flight.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/dsom-automation-encyclopedia-docs-tools/howto-build-sovereign-book.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/dsom-automation-encyclopedia-docs-tools/howto-checkpoint.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/dsom-automation-encyclopedia-docs-tools/howto-checkusage-linux.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/dsom-automation-encyclopedia-docs-tools/howto-checkusage.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/dsom-automation-encyclopedia-docs-tools/howto-dsom-onboard.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/dsom-automation-encyclopedia-docs-tools/howto-eod-palace.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/dsom-automation-encyclopedia-docs-tools/howto-generate-walkthrough.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/dsom-automation-encyclopedia-docs-tools/howto-git-ritual.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/dsom-automation-encyclopedia-docs-tools/howto-hibernation.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/dsom-automation-encyclopedia-docs-tools/howto-init-brain.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/dsom-automation-encyclopedia-docs-tools/howto-palace-sync.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/dsom-automation-encyclopedia-docs-tools/howto-privacy-guardian.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/dsom-automation-encyclopedia-docs-tools/howto-reanimate-claude.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/dsom-automation-encyclopedia-docs-tools/howto-reanimate.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/dsom-automation-encyclopedia-docs-tools/howto-setup-dsom-control-node.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/dsom-automation-encyclopedia-docs-tools/howto-setup-wsl-almalinux.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/dsom-automation-encyclopedia-docs-tools/howto-sod-palace.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/dsom-automation-encyclopedia-docs-tools/howto-template-reset.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/member-spokes-tactical/implementation_plan.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/member-spokes-tactical/palace_registry.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/member-spokes-tactical/walkthrough.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/model-specifics/claude-setup.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/model-specifics/copilot-setup.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/model-specifics/dsom-claude-initialiser.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/model-specifics/howto-create-dsom-gemini-gem.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/palace-documentation/howto-migrate-to-palace.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/palace-documentation/howto-palace-onboarding.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/palace-documentation/howto-port-ai-palace.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/palace-documentation/okf-adoption-guide.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/palace-documentation/palace-build-story.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/palace-documentation/research-reasoning-gap.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/reference-architectures-ansible-blueprint/ansible-config-guide.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/reference-architectures-ansible-blueprint/ansible-control-node-protocol.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/reference-architectures-ansible-blueprint/ansible-deployment-architecture.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/reference-architectures-ansible-blueprint/ansible-inventory-explained.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/reference-architectures-ansible-blueprint/howto-setup-ansible-baseline.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/table-of-contents/changelog.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/table-of-contents/contributing.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/table-of-contents/history.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/table-of-contents/readme.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/table-of-contents/security.md",
    "https://malaysia-open-source-community.gitbook.io/deep-state-of-mind-dsom-protocol-for-my-ai/table-of-contents/start-here.md"
]

def check_url(url: str) -> tuple:
    """Sends a request to verify the URL exists and is not broken.

    Returns:
        tuple: (bool, str) representing (is_success, failure_type)
    """
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False, f"InvalidScheme:{parsed.scheme}"
    if parsed.netloc not in ALLOWED_HOSTS:
        return False, f"DisallowedHost:{parsed.netloc}"

    req = urllib.request.Request(
        url,
        method="GET",
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                return True, "OK"
            return False, f"HTTPStatus:{response.status}"
    except urllib.error.HTTPError as e:
        return False, f"HTTPError:{e.code}"
    except urllib.error.URLError as e:
        return False, f"URLError:{e.reason}"
    except Exception as e:
        return False, f"UnexpectedError:{type(e).__name__}"

def verify_github_pages_url(url: str) -> bool:
    """Checks if a GitHub Pages URL is live, or if its source exists in docs/."""
    # Strict URL validation before checking
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or parsed.netloc != "linuxmalaysia.github.io":
        print(f"[-] Invalid GitHub Pages URL: {url}")
        return False

    is_ok, failure_type = check_url(url)
    if is_ok:
        print(f"[+] GitHub Pages URL OK (Live): {url}")
        return True

    # Fall back to disk verification ONLY when check_url reports HTTP 404
    if failure_type != "HTTPError:404":
        print(f"[-] GitHub Pages URL failed with critical non-404 error ({failure_type}): {url}")
        return False

    # Perform path validation and resolution
    base_url = "https://linuxmalaysia.github.io/ASIMP/"
    if not url.startswith(base_url):
        print(f"[-] GitHub Pages URL does not match base path: {url}")
        return False

    relative_path = url[len(base_url):]
    if not relative_path or relative_path == "index.html":
        relative_path = "index.md"
    else:
        relative_path = relative_path.replace(".html", ".md")

    # Prevent directory traversal and ensure candidate is inside docs/ folder
    docs_dir = os.path.abspath("docs")
    candidate_path = os.path.abspath(os.path.join(docs_dir, relative_path))

    if not candidate_path.startswith(docs_dir + os.sep) and candidate_path != docs_dir:
        print(f"[-] Directory traversal blocked or path outside docs/: {url} -> {candidate_path}")
        return False

    # Require os.path.isfile() rather than merely os.path.exists()
    if os.path.isfile(candidate_path):
        print(f"[+] GitHub Pages URL OK (Source exists on disk, pre-merge): {url} -> {candidate_path}")
        return True

    print(f"[-] GitHub Pages URL does not exist on live site AND has no disk source file: {url}")
    return False

def compare_file_contents(filepath_a: str, filepath_b: str, file_type: str) -> None:
    """Compares the exact text contents of two sitemap files and fails on mismatch."""
    try:
        with open(filepath_a, "r", encoding="utf-8") as fa:
            content_a = f_a_text = fa.read()
        with open(filepath_b, "r", encoding="utf-8") as fb:
            content_b = f_b_text = fb.read()
    except FileNotFoundError as e:
        print(f"[-] Sitemap comparison failed: file missing {e.filename}")
        sys.exit(1)

    if content_a != content_b:
        print(f"[-] Validation Error: Deployed copy {filepath_b} differs from root {filepath_a}!")
        sys.exit(1)
    print(f"[+] Deployed copy {filepath_b} is perfectly synchronized with root {filepath_a} ({file_type}).")

def main() -> None:
    print("[*] Starting Sitemap and Link Integrity Verification...")

    # 1. Compare docs/ sitemaps against root sitemaps to ensure perfect sync before URL verification
    compare_file_contents("sitemap.txt", "docs/sitemap.txt", "txt sitemap")
    compare_file_contents("sitemap.xml", "docs/sitemap.xml", "xml sitemap")

    # 2. Parse and verify sitemap.txt URLs
    try:
        with open("sitemap.txt", "r") as f:
            txt_urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("[-] sitemap.txt not found in root directory!")
        sys.exit(1)

    print(f"[*] Found {len(txt_urls)} URLs in sitemap.txt")

    # 3. Parse and verify sitemap.xml URLs
    try:
        tree = ET.parse("sitemap.xml")
        root = tree.getroot()
        namespace = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        xml_urls = [loc.text for loc in root.findall(".//ns:loc", namespace)]
    except FileNotFoundError:
        print("[-] sitemap.xml not found in root directory!")
        sys.exit(1)
    except ET.ParseError as e:
        print(f"[-] XML parsing failed for sitemap.xml: {e}")
        sys.exit(1)

    print(f"[*] Found {len(xml_urls)} URLs in sitemap.xml")

    # 4. Structural matching checks
    if set(txt_urls) != set(xml_urls):
        print("[-] Mismatch between sitemap.txt and sitemap.xml URL lists!")
        sys.exit(1)
    print("[+] Structural check passed: sitemap.txt and sitemap.xml URL lists match perfectly.")

    # 5. Check sitemap GitHub Pages URLs
    gh_pages_urls = []
    for u in txt_urls:
        parsed = urlparse(u)
        if parsed.netloc == "linuxmalaysia.github.io":
            gh_pages_urls.append(u)
        else:
            print(f"[-] Invalid host in sitemaps: {u} (Only linuxmalaysia.github.io is allowed in sitemaps)")
            sys.exit(1)

    success = True
    print(f"[*] Verifying all {len(gh_pages_urls)} GitHub Pages URLs...")
    for u in gh_pages_urls:
        if not verify_github_pages_url(u):
            success = False

    # 6. Verify GitBook URLs loaded from the separate validation inventory
    print(f"[*] Loading validation inventory of {len(GITBOOK_URLS)} GitBook URLs...")
    print(f"[*] Verifying a sample of 5 GitBook URLs from the inventory to check live routing...")
    random.seed(42) # Deterministic sample selection
    sample_gitbook = random.sample(GITBOOK_URLS, min(5, len(GITBOOK_URLS)))
    for u in sample_gitbook:
        is_ok, failure_type = check_url(u)
        if is_ok:
            print(f"[+] GitBook inventory URL OK (Live): {u}")
        else:
            print(f"[-] GitBook inventory URL FAILED ({failure_type}): {u}")
            success = False

    if not success:
        print("[-] Link verification FAILED! There are broken links or validation failures.")
        sys.exit(1)

    print("[+] All verified sitemap links and inventory URLs are fully operational and synchronized!")

if __name__ == "__main__":
    main()
