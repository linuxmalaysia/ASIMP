#!/usr/bin/env python3
"""Hardened One-Way Docs Sync Script with 5 Strict Safety Guards.

Syncs compiled Mintlify MDX documentation from `docs-source/` to downstream Mintlify deployment repository.
Protected by 5 non-negotiable safety guards:
- Guard A: Source & JSON Integrity
- Guard B: Minimum File Count Floor
- Guard C: Navigation Integrity
- Guard D: Diff Preview & Deletion Cap
- Guard E: Dry-Run Mode
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

# Configuration defaults
DEFAULT_OWNER = "linuxmalaysia"
DEFAULT_DOCS_REPO = "documentation-asimp-ansible-framework"
DEFAULT_SUBDOMAIN = "asimp-ansible-system-integrity-management-platform"
DEFAULT_BRANCH = "main"
DEFAULT_MIN_MDX_FILES = 5
DEFAULT_MAX_DELETIONS = 10


def run_cmd(cmd: List[str], cwd: Path = None, env: Dict[str, str] = None) -> Tuple[int, str, str]:
    """
    Execute a command and capture its exit status, standard output, and standard error.
    
    Parameters:
    	cmd (List[str]): Command and arguments to execute.
    	cwd (Path): Working directory for the command.
    	env (Dict[str, str]): Environment variables for the command.
    
    Returns:
    	Tuple[int, str, str]: The exit code, standard output, and standard error.
    """
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    return proc.returncode, proc.stdout, proc.stderr


def extract_pages_from_nav(nav_node: Any) -> List[str]:
    """Collects page paths from a navigation structure.
    
    Parameters:
    	nav_node (Any): Navigation data containing page paths and nested navigation entries.
    
    Returns:
    	List[str]: Page paths found in the navigation structure.
    """
    pages: List[str] = []
    if isinstance(nav_node, dict):
        if "pages" in nav_node and isinstance(nav_node["pages"], list):
            for item in nav_node["pages"]:
                if isinstance(item, str):
                    pages.append(item)
                else:
                    pages.extend(extract_pages_from_nav(item))
        for key, val in nav_node.items():
            if key != "pages":
                pages.extend(extract_pages_from_nav(val))
    elif isinstance(nav_node, list):
        for item in nav_node:
            pages.extend(extract_pages_from_nav(item))
    return pages


def guard_a_source_and_json_integrity(docs_source_dir: Path) -> Dict[str, Any]:
    """
    Validate the documentation source directory and its configuration file.
    
    Parameters:
    	docs_source_dir (Path): Directory containing the documentation source files.
    
    Returns:
    	Dict[str, Any]: Parsed contents of the directory's ``docs.json`` file.
    """
    print("[Guard A] Checking Source & JSON Integrity...")
    if not docs_source_dir.exists() or not docs_source_dir.is_dir():
        print(f"FAILED Guard A: Source directory '{docs_source_dir}' does not exist.", file=sys.stderr)
        sys.exit(1)

    docs_json_path = docs_source_dir / "docs.json"
    if not docs_json_path.exists():
        print(f"FAILED Guard A: 'docs.json' missing in '{docs_source_dir}'.", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(docs_json_path.read_text(encoding="utf-8"))
        print("[Guard A] PASSED: docs-source/ and valid docs.json found.")
        return data
    except Exception as e:
        print(f"FAILED Guard A: 'docs.json' is invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)


def guard_b_minimum_file_count_floor(docs_source_dir: Path, min_mdx_files: int) -> List[Path]:
    """
    Ensure the documentation source contains the required minimum number of MDX files.
    
    Parameters:
        docs_source_dir (Path): Directory containing the documentation source files.
        min_mdx_files (int): Minimum number of MDX files required.
    
    Returns:
        List[Path]: Paths to all MDX files found recursively.
    """
    print(f"[Guard B] Checking Minimum File Count Floor (min: {min_mdx_files})...")
    mdx_files = list(docs_source_dir.rglob("*.mdx"))
    count = len(mdx_files)
    if count < min_mdx_files:
        print(f"FAILED Guard B: Found {count} .mdx files, which is below floor of {min_mdx_files}.", file=sys.stderr)
        sys.exit(1)

    print(f"[Guard B] PASSED: Found {count} .mdx files (>= {min_mdx_files}).")
    return mdx_files


def guard_c_navigation_integrity(docs_source_dir: Path, docs_json_data: Dict[str, Any]) -> None:
    """
    Validate that every page referenced by the documentation navigation has a corresponding MDX file.
    
    Parameters:
        docs_source_dir (Path): Directory containing the compiled MDX files.
        docs_json_data (Dict[str, Any]): Parsed documentation configuration.
    
    Exits:
        With status 1 if the navigation section is missing or references unavailable pages.
    """
    print("[Guard C] Checking Navigation Integrity...")
    nav = docs_json_data.get("navigation")
    if not nav:
        print("FAILED Guard C: 'navigation' section missing from docs.json.", file=sys.stderr)
        sys.exit(1)

    referenced_pages = extract_pages_from_nav(nav)
    missing_pages: List[str] = []

    for page in referenced_pages:
        page_clean = page if not page.endswith(".mdx") else page[:-4]
        mdx_path = docs_source_dir / f"{page_clean}.mdx"
        if not mdx_path.exists():
            missing_pages.append(page)

    if missing_pages:
        print(f"FAILED Guard C: {len(missing_pages)} page(s) referenced in docs.json do not exist as .mdx files:", file=sys.stderr)
        for mp in missing_pages:
            print(f"  - {mp}", file=sys.stderr)
        sys.exit(1)

    print(f"[Guard C] PASSED: All {len(referenced_pages)} navigation pages exist in docs-source/.")


def get_all_relative_files(base_dir: Path, exclude_git: bool = True) -> Set[Path]:
    """
    Collect relative paths for all files within a directory.
    
    Parameters:
        base_dir (Path): Directory to search.
        exclude_git (bool): Whether to omit files within `.git`.
    
    Returns:
        Set[Path]: Relative file paths found beneath the directory.
    """
    files = set()
    for root, dirs, filenames in os.walk(base_dir):
        rel_root = Path(root).relative_to(base_dir)
        if exclude_git and ".git" in rel_root.parts:
            continue
        for f in filenames:
            rel_file = rel_root / f
            if exclude_git and rel_file.parts[0] == ".git":
                continue
            files.add(rel_file)
    return files


def guard_d_diff_preview_and_deletion_cap(
    docs_source_dir: Path,
    downstream_dir: Path,
    max_deletions: int,
    allow_large_deletions: bool
) -> Tuple[List[Path], List[Path], List[Path]]:
    """
    Compare source and downstream files while enforcing the deletion limit.
    
    Parameters:
        docs_source_dir (Path): Directory containing the source documentation files.
        downstream_dir (Path): Directory containing the downstream files.
        max_deletions (int): Maximum number of deleted files permitted.
        allow_large_deletions (bool): Whether to permit deletions above the limit.
    
    Returns:
        Tuple[List[Path], List[Path], List[Path]]: Added, modified, and deleted relative file paths.
    
    """
    print(f"[Guard D] Computing diff and checking Deletion Cap (max deletions: {max_deletions}, allow large: {allow_large_deletions})...")

    existing_files = get_all_relative_files(downstream_dir)
    new_files = get_all_relative_files(docs_source_dir)

    added = sorted(list(new_files - existing_files))
    deleted = sorted(list(existing_files - new_files))

    common = new_files.intersection(existing_files)
    modified = []
    for rel_f in sorted(list(common)):
        src_f = docs_source_dir / rel_f
        dst_f = downstream_dir / rel_f
        try:
            if src_f.read_bytes() != dst_f.read_bytes():
                modified.append(rel_f)
        except Exception:
            modified.append(rel_f)

    print(f"[Guard D Diff Summary] Added: {len(added)}, Modified: {len(modified)}, Deleted: {len(deleted)}")

    if len(deleted) > max_deletions and not allow_large_deletions:
        print(
            f"FAILED Guard D: Deletions count ({len(deleted)}) exceeds MAX_DELETIONS limit ({max_deletions}). "
            f"Set ALLOW_LARGE_DELETIONS=true if this deletion is intentional.",
            file=sys.stderr
        )
        print("Deleted files:", file=sys.stderr)
        for df in deleted[:20]:
            print(f"  - {df}", file=sys.stderr)
        if len(deleted) > 20:
            print(f"  ... and {len(deleted) - 20} more.", file=sys.stderr)
        sys.exit(1)

    print("[Guard D] PASSED: Diff computed safely within deletion threshold.")
    return added, modified, deleted


def main() -> None:
    """
    Run the documentation synchronization workflow, including validation, safety checks, and optional downstream repository updates.
    
    Command-line arguments and environment variables control dry-run mode, deletion limits, source and downstream locations, repository details, and synchronization settings.
    """
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Hardened One-Way Docs Sync Script")
    parser.add_argument("--dry-run", action="store_true", help="Preview plan without committing or pushing")
    parser.add_argument("--allow-large-deletions", action="store_true", help="Bypass MAX_DELETIONS safety cap")
    parser.add_argument("--min-mdx-files", type=int, default=int(os.environ.get("MIN_MDX_FILES", DEFAULT_MIN_MDX_FILES)))
    parser.add_argument("--max-deletions", type=int, default=int(os.environ.get("MAX_DELETIONS", DEFAULT_MAX_DELETIONS)))
    parser.add_argument("--docs-source-dir", type=str, default="docs-source")
    parser.add_argument("--downstream-dir", type=str, default="", help="Path to local downstream repo if already cloned")
    parser.add_argument("--owner", type=str, default=os.environ.get("DOCS_REPO_OWNER", DEFAULT_OWNER))
    parser.add_argument("--repo", type=str, default=os.environ.get("DOCS_REPO_NAME", DEFAULT_DOCS_REPO))
    parser.add_argument("--subdomain", type=str, default=os.environ.get("SUBDOMAIN", DEFAULT_SUBDOMAIN))
    parser.add_argument("--branch", type=str, default=DEFAULT_BRANCH)

    args = parser.parse_args()

    # Environment overrides
    is_dry_run = args.dry_run or os.environ.get("DRY_RUN", "false").lower() in ("true", "1", "yes")
    allow_large_deletions = args.allow_large_deletions or os.environ.get("ALLOW_LARGE_DELETIONS", "false").lower() in ("true", "1", "yes")
    min_mdx_files = args.min_mdx_files
    max_deletions = args.max_deletions

    docs_source_dir = Path(args.docs_source_dir).resolve()

    # Step 1: Execute Guards A, B, C
    docs_json_data = guard_a_source_and_json_integrity(docs_source_dir)
    guard_b_minimum_file_count_floor(docs_source_dir, min_mdx_files)
    guard_c_navigation_integrity(docs_source_dir, docs_json_data)

    # Prepare downstream repo
    temp_dir_obj = None
    if args.downstream_dir:
        downstream_dir = Path(args.downstream_dir).resolve()
    else:
        token = os.environ.get("DOCS_REPO_TOKEN") or os.environ.get("GITHUB_TOKEN")
        if not token and not is_dry_run:
            print("FAILED: DOCS_REPO_TOKEN or GITHUB_TOKEN environment variable required for sync.", file=sys.stderr)
            sys.exit(1)

        temp_dir_obj = tempfile.TemporaryDirectory()
        downstream_dir = Path(temp_dir_obj.name)

        if token:
            clone_url = f"https://x-access-token:{token}@github.com/{args.owner}/{args.repo}.git"
        else:
            clone_url = f"https://github.com/{args.owner}/{args.repo}.git"

        print(f"Cloning downstream repo {args.owner}/{args.repo} ({args.branch}) into temporary workspace...")
        ret, out, err = run_cmd(["git", "clone", "-b", args.branch, "--single-branch", clone_url, str(downstream_dir)])
        if ret != 0:
            print(f"FAILED to clone downstream repo: {err}", file=sys.stderr)
            sys.exit(1)

    # Step 2: Guard D (Diff Preview & Deletion Cap)
    added, modified, deleted = guard_d_diff_preview_and_deletion_cap(
        docs_source_dir, downstream_dir, max_deletions, allow_large_deletions
    )

    # Step 3: Guard E (Dry-Run Mode)
    print(f"[Guard E] Checking Dry-Run Mode (dry_run: {is_dry_run})...")
    if is_dry_run:
        print("[Guard E] PASSED: Dry-run active. Execution preview complete. No changes written or pushed.")
        if temp_dir_obj:
            temp_dir_obj.cleanup()
        sys.exit(0)

    print("[Guard E] PASSED: Dry-run disabled. Proceeding with sync execution...")

    # Sync Execution Phase
    print("Beginning sync execution...")

    # Wipe downstream working tree (preserve .git)
    for item in downstream_dir.iterdir():
        if item.name == ".git":
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    # Copy docs-source/ into downstream working tree
    for item in docs_source_dir.iterdir():
        target = downstream_dir / item.name
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)

    # Configure Git bot identity
    bot_name = "Docs Sync Bot"
    bot_email = f"bot@{args.subdomain}.mintlify.site"
    run_cmd(["git", "config", "user.name", bot_name], cwd=downstream_dir)
    run_cmd(["git", "config", "user.email", bot_email], cwd=downstream_dir)

    # Stage changes
    run_cmd(["git", "add", "-A"], cwd=downstream_dir)

    ret, status_out, _ = run_cmd(["git", "status", "--porcelain"], cwd=downstream_dir)
    if not status_out.strip():
        print("Downstream working tree is clean. No changes to commit.")
        if temp_dir_obj:
            temp_dir_obj.cleanup()
        sys.exit(0)

    # Get short SHA of source repo
    ret, sha_out, _ = run_cmd(["git", "rev-parse", "--short", "HEAD"])
    short_sha = sha_out.strip() if ret == 0 and sha_out.strip() else "latest"

    commit_msg = f"Sync docs from app repo @ {short_sha}"
    print(f"Committing changes: '{commit_msg}'...")
    ret, out, err = run_cmd(["git", "commit", "-m", commit_msg], cwd=downstream_dir)
    if ret != 0:
        print(f"FAILED to commit changes: {err}", file=sys.stderr)
        sys.exit(1)

    print(f"Pushing commit to {args.owner}/{args.repo} branch {args.branch}...")
    ret, out, err = run_cmd(["git", "push", "origin", args.branch], cwd=downstream_dir)
    if ret != 0:
        print(f"FAILED to push changes to downstream repo: {err}", file=sys.stderr)
        sys.exit(1)

    print(f"Successfully synced docs to {args.owner}/{args.repo} branch {args.branch}.")

    if temp_dir_obj:
        temp_dir_obj.cleanup()


if __name__ == "__main__":
    main()
