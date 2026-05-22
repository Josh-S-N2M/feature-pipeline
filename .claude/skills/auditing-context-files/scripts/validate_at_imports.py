#!/usr/bin/env python3
"""
validate_at_imports.py — Resolve CLAUDE.md @-imports recursively.

Detects:
  - Imports of non-existent files
  - Cycles (A imports B imports A)
  - Excessive depth (>5)
  - Imports targeting paths outside the project root

Usage:
    python3 validate_at_imports.py <path-to-CLAUDE.md> [--project-root <path>]

The project root defaults to the directory containing the CLAUDE.md.
Set explicitly for files outside the project root.
"""
import json
import re
import sys
from pathlib import Path

MAX_DEPTH = 5

# Match @-imports. Examples:
#   @docs/architecture.md
#   @./auth-rules.md
#   @/absolute/path.md
# Capture the path; allow leading slash, dot, or letter.
AT_IMPORT_RE = re.compile(r"(?<!\S)@([\.\/\w][\w\.\-\/]*\.md)\b")


def find_imports_in(text: str) -> list[tuple[int, str]]:
    """Return list of (line_number, path_str) for each @-import."""
    out = []
    for i, line in enumerate(text.split("\n"), start=1):
        for m in AT_IMPORT_RE.finditer(line):
            out.append((i, m.group(1)))
    return out


def resolve_import(current_file: Path, import_str: str, project_root: Path) -> Path:
    """Resolve an @-import string to an absolute path."""
    if import_str.startswith("/"):
        return Path(import_str).resolve()
    if import_str.startswith("./") or import_str.startswith("../"):
        return (current_file.parent / import_str).resolve()
    # No leading slash or dot — resolve relative to current file's directory
    return (current_file.parent / import_str).resolve()


def walk(file: Path, project_root: Path, depth: int, visited: set, findings: list):
    if depth > MAX_DEPTH:
        findings.append({
            "dimension": 2,
            "severity": "BLOCKER",
            "location": str(file),
            "what": f"@-import depth exceeds {MAX_DEPTH}. The chain may be silently truncated or errored.",
            "fix": "Flatten the import chain. Inline imports more than 3 levels deep.",
        })
        return

    if file in visited:
        findings.append({
            "dimension": 2,
            "severity": "BLOCKER",
            "location": str(file),
            "what": "Cycle detected in @-import chain.",
            "fix": "Remove the circular @-import.",
        })
        return

    if not file.is_file():
        findings.append({
            "dimension": 2,
            "severity": "MAJOR",
            "location": str(file),
            "what": f"@-import target does not exist: {file}",
            "fix": "Create the file, fix the path, or remove the import.",
        })
        return

    # Outside project root?
    try:
        file.resolve().relative_to(project_root.resolve())
    except ValueError:
        findings.append({
            "dimension": 2,
            "severity": "MAJOR",
            "location": str(file),
            "what": f"@-import target is outside project root: {file}",
            "fix": "Copy the imported file into the project, or accept that this CLAUDE.md is machine-specific.",
        })
        # Continue walking — we can still detect cycles/depth even outside root
        # but only if the file exists.
        if not file.is_file():
            return

    visited.add(file)
    try:
        text = file.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        findings.append({
            "dimension": 2,
            "severity": "MAJOR",
            "location": str(file),
            "what": f"Could not read @-import target: {e}",
            "fix": "Fix file permissions or content encoding.",
        })
        return

    for line_no, imp_str in find_imports_in(text):
        target = resolve_import(file, imp_str, project_root)
        walk(target, project_root, depth + 1, visited, findings)


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(json.dumps({"error": "Usage: validate_at_imports.py <path-to-CLAUDE.md> [--project-root <path>]"}))
        return 2

    target = Path(args[0]).resolve()
    project_root = target.parent
    if "--project-root" in args:
        idx = args.index("--project-root")
        if idx + 1 < len(args):
            project_root = Path(args[idx + 1]).resolve()

    if not target.is_file():
        print(json.dumps({"error": f"not a file: {target}"}))
        return 2

    findings: list = []
    visited: set = set()
    walk(target, project_root, 0, visited, findings)

    # Attach where for output uniformity
    for f in findings:
        f.setdefault("where", f.get("location", str(target)))

    print(json.dumps({
        "target": str(target),
        "project_root": str(project_root),
        "imports_walked": len(visited),
        "findings": findings,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
