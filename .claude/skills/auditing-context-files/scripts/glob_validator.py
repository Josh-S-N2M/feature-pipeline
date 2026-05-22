#!/usr/bin/env python3
"""
glob_validator.py — Validate `paths:` globs from rules file frontmatter.

Detects:
  - Empty paths list (BLOCKER — rule never loads)
  - Globs that match nothing under the project root (BLOCKER if no matches anywhere)
  - Common syntax mistakes:
    - Windows backslash separators
    - Trailing slash on file patterns
    - Missing leading **/ for ext patterns
    - Bare *.ext that only matches at root

Usage:
    python3 glob_validator.py <path-to-rule.md> [--project-root <path>]
"""
import json
import re
import sys
from pathlib import Path
import fnmatch

try:
    import yaml
except ImportError:
    print(json.dumps({"error": "PyYAML not installed", "findings": []}))
    sys.exit(0)


def parse_frontmatter(text: str) -> dict | None:
    if not text.startswith("---"):
        return None
    lines = text.split("\n")
    if lines[0].strip() != "---":
        return None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            fm_text = "\n".join(lines[1:i])
            try:
                return yaml.safe_load(fm_text)
            except yaml.YAMLError:
                return None
    return None


def is_common_glob_mistake(g: str) -> list[str]:
    """Return list of detected syntax mistakes."""
    issues = []
    if "\\" in g:
        issues.append("Contains backslash (Windows syntax); use forward slashes.")
    if g.endswith("/") and "*" in g.split("/")[-2]:
        issues.append("Trailing slash on a file pattern — matches directories, not files.")
    if "*" in g and "/" not in g and not g.startswith("**"):
        issues.append("Pattern without leading `**/` matches only at project root.")
    return issues


def glob_matches_anything(g: str, project_root: Path) -> bool:
    """Check if the glob matches any actual file in the project."""
    try:
        for _p in project_root.glob(g):
            return True
        # Also try with ** semantics if not present
        if not g.startswith("**"):
            for _p in project_root.glob(f"**/{g}"):
                return True
        return False
    except Exception:
        return False


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(json.dumps({"error": "Usage: glob_validator.py <path-to-rule.md> [--project-root <path>]"}))
        return 2

    target = Path(args[0]).resolve()
    project_root = None
    if "--project-root" in args:
        idx = args.index("--project-root")
        if idx + 1 < len(args):
            project_root = Path(args[idx + 1]).resolve()
    if project_root is None:
        # Try to detect by walking up looking for .claude/ or .git/
        cur = target.parent
        while cur != cur.parent:
            if (cur / ".claude").is_dir() or (cur / ".git").is_dir():
                project_root = cur
                break
            cur = cur.parent
        if project_root is None:
            project_root = target.parent

    if not target.is_file():
        print(json.dumps({"error": f"not a file: {target}"}))
        return 2

    text = target.read_text(encoding="utf-8", errors="replace")
    fm = parse_frontmatter(text)

    findings: list = []
    if fm is None:
        findings.append({
            "dimension": 5,
            "severity": "MAJOR",
            "location": str(target),
            "what": "Rule file has no parseable YAML frontmatter.",
            "fix": "Add frontmatter with `paths:` listing the file patterns this rule applies to.",
        })
        print(json.dumps({"target": str(target), "findings": findings}))
        return 0

    paths = fm.get("paths", [])
    if isinstance(paths, str):
        paths = [paths]
    if not isinstance(paths, list):
        findings.append({
            "dimension": 5,
            "severity": "MAJOR",
            "location": str(target),
            "what": f"`paths:` should be a list; got {type(paths).__name__}.",
            "fix": "Use YAML list syntax: `paths:\\n  - \"**/*.ts\"`.",
        })
        paths = []

    if not paths:
        findings.append({
            "dimension": 5,
            "severity": "BLOCKER",
            "location": str(target),
            "what": "Rule has empty `paths:` list — it will never load.",
            "fix": "Add at least one glob pattern, or move the content to CLAUDE.md if it should always load.",
        })

    for g in paths:
        if not isinstance(g, str):
            findings.append({
                "dimension": 5,
                "severity": "MAJOR",
                "location": str(target),
                "what": f"Non-string glob entry: {g!r}",
                "fix": "Each `paths:` entry must be a string glob pattern.",
            })
            continue

        for issue in is_common_glob_mistake(g):
            findings.append({
                "dimension": 5,
                "severity": "MAJOR",
                "location": str(target),
                "what": f"Glob `{g}`: {issue}",
                "fix": "Adjust the glob syntax. See `references/rules-spec.md` for examples.",
            })

        # Check existence — but only emit BLOCKER if NO pattern in this rule matches anything
    if paths and not any(isinstance(g, str) and glob_matches_anything(g, project_root) for g in paths):
        findings.append({
            "dimension": 5,
            "severity": "BLOCKER",
            "location": str(target),
            "what": f"None of the `paths:` globs match any file under {project_root}.",
            "fix": "Verify the glob syntax and adjust patterns. The rule will never load otherwise.",
        })

    # Empty body check (AP: Description-as-rule)
    body = text.split("---", 2)[-1].strip() if text.count("---") >= 2 else ""
    if not body or len(body) < 30:
        findings.append({
            "dimension": 5,
            "severity": "BLOCKER",
            "location": str(target),
            "what": "Rule body is empty or near-empty. The `description:` field is not used as rule content.",
            "fix": "Add rule content in the body, after the closing `---` of frontmatter.",
        })

    for f in findings:
        f.setdefault("where", f.get("location", str(target)))

    print(json.dumps({
        "target": str(target),
        "paths": paths,
        "findings": findings,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
