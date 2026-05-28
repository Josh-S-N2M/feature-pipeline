#!/usr/bin/env python3
"""
lint_references.py — Verify referenced files exist and check nesting depth.

For each .md file in the skill directory:
  - Find Markdown links: [label](path/to/file.md)
  - Find backticked paths: `references/foo.md` (and similar)
  - Find script execution paths: `python ... scripts/foo.py`

For each reference:
  - Verify the target file exists.
  - Track which file contains the reference.

Then check:
  - Reference Illusion: any link to a file that doesn't exist (BLOCKER).
  - Nesting depth: a reference file linking to another reference file (MAJOR).

Usage:
    python3 lint_references.py <path-to-skill-dir>
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


MD_LINK = re.compile(r"\[([^\]]+)\]\(([^)#\s]+)(?:#[^)]*)?\)")
# Backticked paths: must include a directory separator (`references/foo.md`, `scripts/bar.py`).
# Backticked basenames alone (`foo.md`) are treated as citations, not refs — too noisy.
BACKTICK_PATH = re.compile(r"`((?:[a-zA-Z0-9_.-]+/)+[a-zA-Z0-9_.-]+\.(md|py|sh|json|yaml|yml|txt|html|js)(?:\.example)?)`")
# Script execution: e.g. `python3 ... scripts/foo.py` or `${CLAUDE_SKILL_DIR}/scripts/foo.py`
EXEC_PATH = re.compile(r"(?:python3?\s+|\$\{CLAUDE_SKILL_DIR\}/)([a-zA-Z0-9_./-]+\.py)")
# Inline code spans (between single backticks). Used to mask out fake links inside `[label](path)` examples.
INLINE_CODE = re.compile(r"`[^`\n]*`")
# Shell-like fence languages where EXEC_PATH is meaningful
SHELL_LANGS = {"bash", "sh", "shell", "zsh", "console"}
# TOC heading detection — the property is "navigable index near the top," not a literal heading string.
# Covers Contents, Table of contents, In this file/document/reference, On this page, What's here/inside,
# Sections, Outline. H2 or H3 level. Case-insensitive.
TOC_HEADING = re.compile(
    r"^#{2,3}\s+("
    r"contents?|"
    r"table of contents?|"
    r"in this (file|document|reference)|"
    r"on this page|"
    r"what(?:'?s| is) (in this|here|inside)|"
    r"sections?|"
    r"outline"
    r")\s*$",
    re.IGNORECASE | re.MULTILINE,
)


def collect_references(file: Path, skill_dir: Path) -> list[tuple[str, int]]:
    """Return [(referenced_path, line_no), ...] from this file.

    Outside fences: all three patterns (MD_LINK, BACKTICK_PATH, EXEC_PATH).
    Inside shell fences (bash/sh/zsh/shell/console): EXEC_PATH only (real commands).
    Inside non-shell fences (markdown, yaml, python, etc.): nothing — example content.
    Inline code spans (`...`) are masked before MD_LINK matching.
    """
    refs: list[tuple[str, int]] = []
    try:
        text = file.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return refs

    in_fence = False
    fence_lang = ""
    for lineno, line in enumerate(text.splitlines(), start=1):
        stripped = line.lstrip()
        if stripped.startswith("```"):
            if in_fence:
                in_fence = False
                fence_lang = ""
            else:
                in_fence = True
                fence_lang = stripped[3:].strip().lower()
            continue

        if not in_fence:
            # Mask inline code spans so [label](path) inside backticks doesn't match MD_LINK
            masked = INLINE_CODE.sub(lambda m: " " * len(m.group(0)), line)
            for m in MD_LINK.finditer(masked):
                target = m.group(2)
                if target.startswith(("http://", "https://", "mailto:")):
                    continue
                refs.append((target, lineno))
            for m in BACKTICK_PATH.finditer(line):
                refs.append((m.group(1), lineno))
            for m in EXEC_PATH.finditer(line):
                refs.append((m.group(1), lineno))
        elif fence_lang in SHELL_LANGS:
            # Real shell commands inside ```bash blocks
            for m in EXEC_PATH.finditer(line):
                refs.append((m.group(1), lineno))
        # else: inside non-shell fence — pedagogical content, skip

    return refs


_REPO_MARKERS = (".git", ".claude", "adrs")


def _find_repo_root(start: Path) -> Path | None:
    for parent in [start, *start.parents]:
        if all((parent / m).exists() for m in (".git", ".claude")):
            return parent
        if (parent / ".git").exists():
            return parent
    return None


def normalize(path: str, owner_file: Path, skill_dir: Path) -> Path:
    """Resolve a referenced path. Skill markdown typically uses skill-root-relative paths,
    so we try that first, then fall back to owner-file-relative.

    Cross-KB references (paths starting with `KB-`) get a third resolution attempt:
    try `<skills-root>/<path>` where skills-root is the parent of the current skill_dir.

    Repo-root-relative references (paths starting with `.claude/`, `.devcontainer/`,
    `.github/`, `Issues/`, `adrs/`, `working/`, or any other top-level repo path) get a
    final resolution attempt against the repo root, discovered by walking up from
    skill_dir until a `.git` directory is found. This supports the common documentation
    convention of writing paths relative to the workspace root rather than forcing
    authors to use ../-laden relative paths."""
    p = Path(path)
    if p.is_absolute():
        return p
    if path.startswith("${CLAUDE_SKILL_DIR}/"):
        return skill_dir / path[len("${CLAUDE_SKILL_DIR}/"):]
    # Cross-KB reference: `KB-foo/references/bar.md` resolves against the skills root
    # (the directory containing all KB-* directories), not the current skill_dir.
    if path.startswith("KB-"):
        skills_root = skill_dir.parent  # e.g. .claude/skills/
        cross_kb = (skills_root / path).resolve()
        if cross_kb.exists():
            return cross_kb
    # Try skill_dir-relative first (the common skill convention)
    skill_relative = (skill_dir / path).resolve()
    if skill_relative.exists():
        return skill_relative
    # Try owner-file-relative
    owner_relative = (owner_file.parent / path).resolve()
    if owner_relative.exists():
        return owner_relative
    # Repo-root-relative fallback (paths like '.claude/agents/foo.md' or 'Issues/bar/baz.md')
    repo_root = _find_repo_root(skill_dir)
    if repo_root is not None:
        repo_relative = (repo_root / path).resolve()
        if repo_relative.exists():
            return repo_relative
    # Skills-root-relative fallback (paths like 'recipe-feature-pipeline/SKILL.md' or
    # 'auditing-shared/scripts/log_state_transition.py' that omit the '.claude/skills/' prefix)
    skills_root = skill_dir.parent
    skills_root_relative = (skills_root / path).resolve()
    if skills_root_relative.exists():
        return skills_root_relative
    # Nothing resolved; return owner-relative as the canonical "this is broken" path
    return owner_relative


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: lint_references.py <skill-dir>", "findings": []}))
        return 2

    skill_dir = Path(sys.argv[1]).expanduser().resolve()
    if not skill_dir.is_dir():
        print(json.dumps({"error": f"not a directory: {skill_dir}", "findings": []}))
        return 2

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        print(json.dumps({"error": "SKILL.md not found", "findings": []}))
        return 2

    findings: list[dict] = []
    referenced_paths: set[str] = set()  # for orphan detection by audit_skill.py

    # First pass: gather all references from SKILL.md
    skill_refs = collect_references(skill_md, skill_dir)
    skill_md_targets: set[Path] = set()

    for target, lineno in skill_refs:
        resolved = normalize(target, skill_md, skill_dir)
        try:
            rel = str(resolved.relative_to(skill_dir))
            referenced_paths.add(rel)
        except ValueError:
            rel = target  # outside the skill dir; rare but possible
        skill_md_targets.add(resolved)

        if not resolved.exists():
            findings.append({
                "severity": "BLOCKER",
                "location": f"SKILL.md:{lineno}",
                "what": f"SKILL.md links to {target!r} (line {lineno}) but the file does not exist (Reference Illusion).",
                "fix": "Either create the file, inline the content into SKILL.md, or remove the broken link.",
            })

    # Second pass: check reference files for depth-2 nesting
    for ref_file in skill_dir.rglob("*.md"):
        if ref_file == skill_md:
            continue
        # Only consider files actually referenced from SKILL.md (others are orphans, handled elsewhere)
        if ref_file.resolve() not in skill_md_targets:
            continue

        nested_refs = collect_references(ref_file, skill_dir)
        for target, lineno in nested_refs:
            resolved = normalize(target, ref_file, skill_dir)
            try:
                rel = str(resolved.relative_to(skill_dir))
                referenced_paths.add(rel)
            except ValueError:
                rel = target

            if not resolved.exists():
                # SK-broken-link severity tiering (ADR-0068).
                # Broken refs in reference files (under references/) are MAJOR,
                # not BLOCKER — the body of a SKILL.md is load-bearing for
                # routing, but ref files are typically instructional and a
                # broken pointer there is less severe.
                rel_str = str(ref_file.relative_to(skill_dir))
                severity = "MAJOR" if rel_str.startswith("references/") else "BLOCKER"
                findings.append({
                    "severity": severity,
                    "what": f"{ref_file.relative_to(skill_dir)} links to {target!r} (line {lineno}) but the file does not exist.",
                    "fix": "Either create the file or fix/remove the link.",
                })
                continue

            # Depth-2 check: this is a reference file linking to another file
            # Allowed if the target is also linked from SKILL.md (cross-reference).
            # Cross-KB references (resolved outside skill_dir) are not depth-2 nesting —
            # they're inter-skill navigation and have different ergonomics.
            try:
                resolved.relative_to(skill_dir)
                within_skill = True
            except ValueError:
                within_skill = False
            if within_skill and resolved.suffix == ".md" and resolved != skill_md and resolved not in skill_md_targets:
                findings.append({
                    "severity": "MAJOR",
                    "what": f"{ref_file.relative_to(skill_dir)} links to {target!r} (depth-2 nesting). Claude may partial-read it.",
                    "fix": f"Add a direct link from SKILL.md to {target!r}, or inline the content.",
                })

        # Long files without TOC
        line_count = sum(1 for _ in ref_file.open(encoding="utf-8", errors="replace"))
        if line_count > 100:
            content = ref_file.read_text(encoding="utf-8", errors="replace")
            if not TOC_HEADING.search(content):
                severity = "MAJOR" if line_count > 300 else "MINOR"
                findings.append({
                    "severity": severity,
                    "what": f"{ref_file.relative_to(skill_dir)} is {line_count} lines but has no recognized table-of-contents heading near the top.",
                    "fix": "Add a heading like `## Contents`, `## Table of contents`, `## In this file`, `## On this page`, or `## Sections` listing the file's sections. The property is navigable-index-near-the-top, not a specific heading string.",
                })

    print(json.dumps({
        "findings": findings,
        "referenced_paths": sorted(referenced_paths),
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
