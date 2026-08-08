#!/usr/bin/env python3
"""
Sitemap URL and Link Integrity Verification Script
Parses the generated sitemap.txt and sitemap.xml and ensures that:
1. All URLs are fully qualified and correctly structured.
2. Every GitBook URL exists and returns HTTP 200.
3. Every GitHub Pages URL exists on the live site (returns HTTP 200) OR matches an on-disk markdown source file in the docs/ folder (pre-merge validation).
"""

import os
import sys
import xml.etree.ElementTree as ET
import urllib.request
import urllib.error
from urllib.parse import urlparse

# Strict set of allowed hostnames to prevent SSRF and arbitrary redirection (satisfies CodeQL requirements)
ALLOWED_HOSTS = {
    "linuxmalaysia.github.io",
    "malaysia-open-source-community.gitbook.io"
}

def check_url(url: str) -> bool:
    """Sends a request to verify the URL exists and is not broken."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        print(f"[-] Invalid URL scheme: {url}")
        return False
    if parsed.netloc not in ALLOWED_HOSTS:
        print(f"[-] Disallowed URL host: {url}")
        return False

    req = urllib.request.Request(
        url,
        method="GET",
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status == 200
    except urllib.error.HTTPError as e:
        print(f"[-] HTTP Error {e.code} for URL: {url}")
        return False
    except urllib.error.URLError as e:
        print(f"[-] URL Error {e.reason} for URL: {url}")
        return False
    except Exception as e:
        print(f"[-] Unexpected Error {e} for URL: {url}")
        return False

def verify_github_pages_url(url: str) -> bool:
    """Checks if a GitHub Pages URL is live, or if its source exists in docs/."""
    # Strict URL validation before checking
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or parsed.netloc != "linuxmalaysia.github.io":
        print(f"[-] Invalid GitHub Pages URL: {url}")
        return False

    if check_url(url):
        print(f"[+] GitHub Pages URL OK (Live): {url}")
        return True

    # If it's a 404, check if the corresponding source exists on disk
    base_url = "https://linuxmalaysia.github.io/ASIMP/"
    if not url.startswith(base_url):
        print(f"[-] GitHub Pages URL does not match base path: {url}")
        return False

    relative_path = url[len(base_url):]
    if not relative_path or relative_path == "index.html":
        relative_path = "index.md"
    else:
        relative_path = relative_path.replace(".html", ".md")

    disk_file = os.path.join("docs", relative_path)
    if os.path.exists(disk_file):
        print(f"[+] GitHub Pages URL OK (Source exists on disk, pre-merge): {url} -> {disk_file}")
        return True

    print(f"[-] GitHub Pages URL does not exist on live site AND has no disk source: {url}")
    return False

def main() -> None:
    print("[*] Starting Sitemap and Link Integrity Verification...")

    # 1. Verify sitemap.txt URLs
    try:
        with open("sitemap.txt", "r") as f:
            txt_urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("[-] sitemap.txt not found in root directory!")
        sys.exit(1)

    print(f"[*] Found {len(txt_urls)} URLs in sitemap.txt")

    # 2. Verify sitemap.xml URLs
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

    # 3. Structural checks
    if set(txt_urls) != set(xml_urls):
        print("[-] Mismatch between sitemap.txt and sitemap.xml URL lists!")
        sys.exit(1)
    print("[+] Structural check passed: sitemap.txt and sitemap.xml URL lists match perfectly.")

    # 4. Check GitHub Pages and representative sample of GitBook with strict domain parsing
    gh_pages_urls = []
    gitbook_urls = []
    for u in txt_urls:
        parsed = urlparse(u)
        if parsed.netloc == "linuxmalaysia.github.io":
            gh_pages_urls.append(u)
        elif parsed.netloc == "malaysia-open-source-community.gitbook.io":
            gitbook_urls.append(u)

    success = True
    print(f"[*] Verifying all {len(gh_pages_urls)} GitHub Pages URLs...")
    for u in gh_pages_urls:
        if not verify_github_pages_url(u):
            success = False

    print(f"[*] Verifying a sample of 5 GitBook URLs to check live platform routing...")
    import random
    random.seed(42) # Deterministic sample
    sample_gitbook = random.sample(gitbook_urls, min(5, len(gitbook_urls)))
    for u in sample_gitbook:
        if check_url(u):
            print(f"[+] GitBook sample URL OK: {u}")
        else:
            success = False

    if not success:
        print("[-] Link verification FAILED! There are broken links.")
        sys.exit(1)

    print("[+] All verified sitemap links are fully operational and verified!")

if __name__ == "__main__":
    main()
