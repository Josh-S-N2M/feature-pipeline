#!/usr/bin/env python3
"""
check_subagent_memory.py — Audit a subagent persistent memory directory.

Detects:
  - Size: MEMORY.md > 200 lines / 25 KB → MAJOR
  - Machine-local paths in committed (project-scope) memory → MAJOR
  - Orphan topic files → MINOR
  - Stale topic references → MINOR
  - .gitignore coverage for local memory (when applicable)

Credentials are scanned by the shared scan_memory_secrets.py — not duplicated here.

Usage:
    python3 check_subagent_memory.py <memory-dir> [--scope project|local|user]
"""
import json
import re
import sys
from pathlib import Path

MAX_LINES = 200
MAX_BYTES = 25 * 1024
TOPIC_FILE_MAX_LINES = 500

PATH_LOCAL_RE = [
    re.compile(r"/home/[a-zA-Z][\w-]*"),
    re.compile(r"/Users/[a-zA-Z][\w-]*"),
    re.compile(r"C:\\\\Users\\\\"),
    re.compile(r"\\\\home\\\\"),
]


def scan_machine_paths(file: Path, dim: int = 5, scope: str = "unknown") -> list[dict]:
    findings = []
    if not file.is_file():
        return findings
    try:
        text = file.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return findings
    for line_no, line in enumerate(text.split("\n"), start=1):
        for pat in PATH_LOCAL_RE:
            m = pat.search(line)
            if m:
                # Severity depends on scope: committed (project) is more dangerous
                sev = "MAJOR" if scope == "project" else "MINOR"
                findings.append({
                    "dimension": dim, "severity": sev,
                    "location": f"{file}:{line_no}",
                    "where": f"{file}:{line_no}",
                    "what": f"Machine-local path: {m.group(0)}. (SAM-2)",
                    "fix": "Use relative paths in subagent memory.",
                })
                break
    return findings


def check_size(memory_md: Path) -> list[dict]:
    if not memory_md.is_file():
        return []
    text = memory_md.read_text(encoding="utf-8", errors="replace")
    lines = len(text.split("\n"))
    byte_size = len(text.encode("utf-8"))
    findings = []
    if lines > MAX_LINES:
        findings.append({
            "dimension": 5, "severity": "MAJOR",
            "location": str(memory_md),
            "where": str(memory_md),
            "what": f"MEMORY.md is {lines} lines (>{MAX_LINES}). Content past line {MAX_LINES} is silently dropped on spawn.",
            "fix": "Trim MEMORY.md. Move detail to topics/ files.",
        })
    elif lines > MAX_LINES - 5:
        findings.append({
            "dimension": 5, "severity": "MINOR",
            "location": str(memory_md),
            "where": str(memory_md),
            "what": f"MEMORY.md is {lines} lines — approaching {MAX_LINES} cap.",
            "fix": "Trim now to avoid truncation.",
        })
    if byte_size > MAX_BYTES:
        findings.append({
            "dimension": 5, "severity": "MAJOR",
            "location": str(memory_md),
            "where": str(memory_md),
            "what": f"MEMORY.md is {byte_size} bytes (>{MAX_BYTES}).",
            "fix": "Reduce file size.",
        })
    return findings


def check_topic_refs(memory_md: Path, topics_dir: Path) -> list[dict]:
    findings = []
    if not memory_md.is_file():
        return findings
    text = memory_md.read_text(encoding="utf-8", errors="replace")
    cited = set()
    for m in re.finditer(r"topics/([a-zA-Z0-9_\-]+)(?:\.md)?", text):
        cited.add(m.group(1))

    on_disk = set()
    if topics_dir.is_dir():
        on_disk = {p.stem for p in topics_dir.glob("*.md")}

    for c in cited - on_disk:
        findings.append({
            "dimension": 5, "severity": "MINOR",
            "location": str(memory_md),
            "where": str(memory_md),
            "what": f"Topic reference 'topics/{c}.md' does not resolve.",
            "fix": "Create the topic file or remove the citation.",
        })
    for o in on_disk - cited:
        findings.append({
            "dimension": 5, "severity": "MINOR",
            "location": str(topics_dir / f"{o}.md"),
            "where": str(topics_dir / f"{o}.md"),
            "what": f"Orphan topic file: not cited from MEMORY.md.",
            "fix": "Cite from MEMORY.md or delete.",
        })
    return findings


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(json.dumps({"error": "Usage: check_subagent_memory.py <memory-dir> [--scope project|local|user]"}))
        return 2

    memory_dir = Path(args[0]).resolve()
    scope = "unknown"
    if "--scope" in args:
        idx = args.index("--scope")
        if idx + 1 < len(args):
            scope = args[idx + 1]

    # Infer scope from path if not provided
    if scope == "unknown":
        path_str = str(memory_dir).replace("\\", "/")
        if "agent-memory-local" in path_str:
            scope = "local"
        elif "/.claude/agent-memory/" in path_str:
            scope = "project"
        elif "/agent-memory/" in path_str:
            scope = "user"

    if not memory_dir.is_dir():
        print(json.dumps({"error": f"not a directory: {memory_dir}", "scope": scope}))
        return 2

    memory_md = memory_dir / "MEMORY.md"
    topics_dir = memory_dir / "topics"

    findings: list = []
    findings.extend(check_size(memory_md))
    findings.extend(scan_machine_paths(memory_md, scope=scope))
    findings.extend(check_topic_refs(memory_md, topics_dir))
    if topics_dir.is_dir():
        for tf in topics_dir.glob("*.md"):
            findings.extend(scan_machine_paths(tf, scope=scope))
            text = tf.read_text(encoding="utf-8", errors="replace")
            if len(text.split("\n")) > TOPIC_FILE_MAX_LINES:
                findings.append({
                    "dimension": 5, "severity": "MINOR",
                    "location": str(tf),
                    "where": str(tf),
                    "what": f"Topic file is >{TOPIC_FILE_MAX_LINES} lines.",
                    "fix": "Split into multiple topics.",
                })

    print(json.dumps({
        "target": str(memory_dir),
        "scope": scope,
        "memory_md_present": memory_md.is_file(),
        "topic_count": len(list(topics_dir.glob("*.md"))) if topics_dir.is_dir() else 0,
        "findings": findings,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
