#!/usr/bin/env python3
"""Mintlify MDX Compiler and Navigation Generator.

Traverses source markdown directories (`docs/`, `.agents/skills/`, `skills/`),
parses OKF/YAML frontmatter, converts standard Markdown to Mintlify MDX,
and dynamically constructs `docs-source/docs.json` with structured navigation.
"""

import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
SKILLS_DIR = PROJECT_ROOT / "skills"
AGENTS_SKILLS_DIR = PROJECT_ROOT / ".agents" / "skills"
OUTPUT_DIR = PROJECT_ROOT / "docs-source"


def parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """Extract YAML frontmatter and body from Markdown text."""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1])
                if isinstance(fm, dict):
                    return fm, parts[2].strip()
            except Exception:
                pass
    return {}, content.strip()


def extract_title_and_description(fm: Dict[str, Any], body: str, fallback_title: str) -> Tuple[str, str]:
    """
    Determine a document's title and description from its frontmatter or body content.
    
    Parameters:
        fm (Dict[str, Any]): Frontmatter metadata.
        body (str): Document body used to derive missing metadata.
        fallback_title (str): Title used when the frontmatter and body contain no title.
    
    Returns:
        Tuple[str, str]: The document title and description.
    """
    title = fm.get("title")
    if not title:
        # Search for first H1 in body
        match = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
        if match:
            title = match.group(1).strip()
        else:
            title = fallback_title

    description = fm.get("description")
    if not description:
        # Check topics or first non-header line
        topics = fm.get("topics")
        if isinstance(topics, list) and topics:
            description = f"Topics: {', '.join(str(t) for t in topics)}"
        else:
            for line in body.splitlines():
                line_s = line.strip()
                if line_s and not line_s.startswith("#") and not line_s.startswith("---") and not line_s.startswith("ASIMP"):
                    description = line_s[:160]
                    break
    if not description:
        description = title

    return str(title), str(description)


def convert_md_to_mdx(fm: Dict[str, Any], body: str, fallback_title: str) -> str:
    """
    Convert Markdown content and YAML frontmatter into Mintlify-compatible MDX.
    
    Parameters:
        fallback_title (str): Title to use when the source content does not provide one.
    
    Returns:
        str: MDX content with normalized title and description frontmatter.
    """
    title, description = extract_title_and_description(fm, body, fallback_title)

    # Sanitize title and description for YAML frontmatter
    clean_title = json.dumps(title)
    clean_desc = json.dumps(description)

    mdx_frontmatter = f"---\ntitle: {clean_title}\ndescription: {clean_desc}\n---"

    mdx_body = body

    return f"{mdx_frontmatter}\n\n{mdx_body}\n"


def discover_files() -> List[Tuple[Path, str]]:
    """Discover Markdown files and map each source path to its output MDX path.
    
    Returns:
        List[Tuple[Path, str]]: Source paths paired with relative target MDX paths.
    """
    discovered: List[Tuple[Path, str]] = []

    # 1. Traverse docs/
    if DOCS_DIR.exists():
        for path in sorted(DOCS_DIR.rglob("*.md")):
            rel_path = path.relative_to(DOCS_DIR)
            rel_str = str(rel_path)
            target_rel = rel_str[:-3] + ".mdx"
            discovered.append((path, target_rel))

    # 2. Traverse skills/ if exists
    if SKILLS_DIR.exists():
        for path in sorted(SKILLS_DIR.rglob("*.md")):
            rel_path = path.relative_to(SKILLS_DIR)
            target_rel = str(Path("skills") / rel_path)[:-3] + ".mdx"
            discovered.append((path, target_rel))

    # 3. Traverse .agents/skills/
    if AGENTS_SKILLS_DIR.exists():
        for path in sorted(AGENTS_SKILLS_DIR.rglob("*.md")):
            rel_path = path.relative_to(AGENTS_SKILLS_DIR)
            if rel_path.name.upper() == "SKILL.MD":
                skill_name = rel_path.parent.name
                target_rel = f"skills/{skill_name}.mdx"
            else:
                target_rel = f"skills/{rel_path}"[:-3] + ".mdx"
            discovered.append((path, target_rel))

    return discovered


def categorize_page(page_path: str) -> str:
    """
    Assign a documentation page to its navigation group based on its path.
    
    Parameters:
        page_path (str): Documentation page path to categorize.
    
    Returns:
        str: Navigation group name assigned to the page.
    """
    norm = page_path.replace("\\", "/")

    if norm.startswith("tutorials/"):
        return "Tutorials"
    elif norm.startswith("how-to/"):
        return "How-To Guides"
    elif norm.startswith("reference/"):
        return "Reference"
    elif norm.startswith("explanation/"):
        return "Explanation & Architecture"
    elif norm.startswith("skills/"):
        return "Agent Skills"
    elif norm in ["openscap", "lynis", "output_openscap", "output_lynis", "output_asimp", "security_posture_assessment"]:
        return "Security Engines & Auditing"
    elif norm in ["architecture", "configuration", "troubleshooting", "ansible_playbook_map", "ansible_fqcn", "podman_rootless", "local_testing_matrix_spec"]:
        return "Core Architecture & Config"
    elif norm in ["ai_agents", "dsom_ansible_review", "sop_knowledge_first_discovery", "legal-notice"]:
        return "Governance & AI Protocol"
    else:
        return "Get Started"


def build_docs_json(pages_rel: List[str]) -> Dict[str, Any]:
    """
    Builds the Mintlify documentation configuration with pages organized into navigation groups.
    
    Parameters:
        pages_rel (List[str]): Relative paths of documentation pages to include.
    
    Returns:
        Dict[str, Any]: Mintlify configuration containing branding, repository navigation, metadata, and ordered page groups.
    """
    groups_dict: Dict[str, List[str]] = {}

    group_order = [
        "Get Started",
        "Core Architecture & Config",
        "Tutorials",
        "How-To Guides",
        "Reference",
        "Explanation & Architecture",
        "Security Engines & Auditing",
        "Governance & AI Protocol",
        "Agent Skills"
    ]

    for page in pages_rel:
        group_name = categorize_page(page)
        groups_dict.setdefault(group_name, []).append(page)

    groups_list = []
    for g_name in group_order:
        if g_name in groups_dict and groups_dict[g_name]:
            groups_list.append({
                "group": g_name,
                "pages": groups_dict[g_name]
            })

    for g_name, p_list in groups_dict.items():
        if g_name not in group_order and p_list:
            groups_list.append({
                "group": g_name,
                "pages": p_list
            })

    config = {
        "$schema": "https://mintlify.com/docs.json",
        "theme": "aspen",
        "name": "Automated Linux Security Hardening Platform (ASIMP)",
        "colors": {
            "primary": "#eb0404",
            "light": "#8b0404",
            "dark": "#db3131"
        },
        "favicon": "https://media.brand.dev/a694c066-2152-4a30-98c8-68562ca26cc9.png",
        "logo": {
            "light": "https://media.brand.dev/497513f9-6ee4-47f8-ac70-8d3024e53056.webp",
            "dark": "https://media.brand.dev/497513f9-6ee4-47f8-ac70-8d3024e53056.webp"
        },
        "navbar": {
            "primary": {
                "type": "github",
                "href": "https://github.com/linuxmalaysia/ASIMP"
            }
        },
        "navigation": {
            "tabs": [
                {
                    "tab": "Product Guide",
                    "groups": groups_list
                }
            ]
        },
        "description": "ASIMP is an open-source, Ansible-powered framework for automated Linux security hardening, compliance auditing, and system integrity monitoring."
    }

    return config


def main() -> None:
    """Main execution function for compiling Mintlify MDX documentation."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print(f"Building Mintlify MDX documentation into {OUTPUT_DIR}...")

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    files = discover_files()
    page_paths: List[str] = []

    for src_path, target_rel in files:
        target_path = OUTPUT_DIR / target_rel
        target_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            content = src_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error reading {src_path}: {e}", file=sys.stderr)
            continue

        fallback_title = src_path.stem.replace("-", " ").replace("_", " ").title()
        fm, body = parse_frontmatter(content)
        mdx_content = convert_md_to_mdx(fm, body, fallback_title)

        target_path.write_text(mdx_content, encoding="utf-8")

        page_entry = target_rel[:-4].replace("\\", "/")
        if page_entry not in page_paths:
            page_paths.append(page_entry)

    page_paths.sort()

    docs_json_data = build_docs_json(page_paths)
    docs_json_path = OUTPUT_DIR / "docs.json"
    docs_json_path.write_text(json.dumps(docs_json_data, indent=2), encoding="utf-8")

    print(f"Successfully compiled {len(files)} MDX files and generated docs.json.")


if __name__ == "__main__":
    main()
