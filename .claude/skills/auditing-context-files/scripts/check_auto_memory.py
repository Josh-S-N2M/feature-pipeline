#!/usr/bin/env python3
"""
check_auto_memory.py — Audit auto-memory at ~/.claude/projects/<id>/memory/.

Detects:
  - Size: MEMORY.md > 200 lines / 25 KB → MAJOR (content past cap is dropped)
  - Per-topic file size > 500 lines → MINOR
  - Machine-local paths in any memory file → MAJOR
  - Stale references: MEMORY.md cites a topic file that doesn't exist → MINOR
  - Orphan topics: file in topics/ not cited from MEMORY.md → MINOR
  - Project-file citations that no longer resolve → MINOR (project-root required)

Usage:
    python3 check_auto_memory.py <path-to-memory-dir> [--project-root <path>]

The memory directory should contain MEMORY.md and optionally a topics/ subdir.
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


def scan_machine_paths(file: Path, dim: int = 6) -> list[dict]:
    findings = []
    try:
        text = file.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return findings
    for line_no, line in enumerate(text.split("\n"), start=1):
        for pat in PATH_LOCAL_RE:
            m = pat.search(line)
            if m:
                findings.append({
                    "dimension": dim,
                    "severity": "MAJOR",
                    "location": f"{file}:{line_no}",
                    "what": f"Machine-local path: {m.group(0)} (AM-5).",
                    "fix": "Use relative paths instead of absolute paths in memory files.",
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
            "dimension": 9,
            "severity": "MAJOR",
            "location": str(memory_md),
            "what": f"MEMORY.md is {lines} lines (>{MAX_LINES}). Content past line {MAX_LINES} is silently dropped at session load. (AM-6)",
            "fix": "Run `/memory prune` or rewrite to fit. Move detail to topics/ files.",
        })
    elif lines > MAX_LINES - 5:
        findings.append({
            "dimension": 9,
            "severity": "MINOR",
            "location": str(memory_md),
            "what": f"MEMORY.md is {lines} lines — approaching {MAX_LINES} cap.",
            "fix": "Trim now to avoid truncation in future sessions.",
        })
    if byte_size > MAX_BYTES:
        findings.append({
            "dimension": 9,
            "severity": "MAJOR",
            "location": str(memory_md),
            "what": f"MEMORY.md is {byte_size} bytes (>{MAX_BYTES}). Content past the cap is silently dropped.",
            "fix": "Reduce file size; move detail to topics/ files.",
        })
    return findings


def check_topic_files(topics_dir: Path) -> list[dict]:
    findings = []
    if not topics_dir.is_dir():
        return findings
    for tf in topics_dir.glob("*.md"):
        if not tf.is_file():
            continue
        text = tf.read_text(encoding="utf-8", errors="replace")
        lines = len(text.split("\n"))
        if lines > TOPIC_FILE_MAX_LINES:
            findings.append({
                "dimension": 9,
                "severity": "MINOR",
                "location": str(tf),
                "what": f"Topic file is {lines} lines (>{TOPIC_FILE_MAX_LINES}). Expensive to read on-demand. (AM-7)",
                "fix": "Split into multiple topic files.",
            })
    return findings


def check_topic_references(memory_md: Path, topics_dir: Path) -> list[dict]:
    findings = []
    if not memory_md.is_file():
        return findings
    text = memory_md.read_text(encoding="utf-8", errors="replace")
    # Find references to topics/<name>.md or topics/<name>
    cited = set()
    for m in re.finditer(r"topics/([a-zA-Z0-9_\-]+)(?:\.md)?", text):
        cited.add(m.group(1))

    # Files on disk
    if topics_dir.is_dir():
        on_disk = {p.stem for p in topics_dir.glob("*.md")}
    else:
        on_disk = set()

    # Stale references: cited but not on disk
    for c in cited - on_disk:
        findings.append({
            "dimension": 7,
            "severity": "MINOR",
            "location": str(memory_md),
            "what": f"Topic reference 'topics/{c}.md' does not resolve to a file on disk. (AM-3)",
            "fix": "Either create the topic file or remove the citation.",
        })

    # Orphan topic files: on disk but not cited
    for o in on_disk - cited:
        findings.append({
            "dimension": 9,
            "severity": "MINOR",
            "location": str(topics_dir / f"{o}.md"),
            "what": f"Topic file `{o}.md` is not cited from MEMORY.md. (AM-4)",
            "fix": "Either add a citation from MEMORY.md or delete the orphan topic file.",
        })

    return findings


def check_project_file_citations(memory_md: Path, project_root: Path | None) -> list[dict]:
    findings = []
    if project_root is None or not memory_md.is_file():
        return findings
    text = memory_md.read_text(encoding="utf-8", errors="replace")
    # Heuristic: look for backticked paths that look like file paths
    for m in re.finditer(r"`([a-zA-Z0-9_\-/\.]+\.[a-zA-Z]{1,5})`", text):
        candidate = m.group(1)
        # Skip URLs and other obvious non-file strings
        if "/" not in candidate and "." not in candidate:
            continue
        if candidate.startswith("http") or candidate.startswith("/etc"):
            continue
        # Try to resolve relative to project root
        resolved = (project_root / candidate)
        if not resolved.is_file():
            # Also try without leading ./
            if not (project_root / candidate.lstrip("./")).is_file():
                findings.append({
                    "dimension": 7,
                    "severity": "MINOR",
                    "location": str(memory_md),
                    "what": f"Citation `{candidate}` does not resolve to a project file.",
                    "fix": "Verify the path; the file may have been moved or deleted. User can `/memory edit` to update.",
                })
    return findings


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(json.dumps({"error": "Usage: check_auto_memory.py <memory-dir> [--project-root <path>]"}))
        return 2

    memory_dir = Path(args[0]).resolve()
    project_root = None
    if "--project-root" in args:
        idx = args.index("--project-root")
        if idx + 1 < len(args):
            project_root = Path(args[idx + 1]).resolve()

    if not memory_dir.is_dir():
        print(json.dumps({"error": f"not a directory: {memory_dir}"}))
        return 2

    memory_md = memory_dir / "MEMORY.md"
    topics_dir = memory_dir / "topics"

    findings: list = []
    findings.extend(check_size(memory_md))
    findings.extend(scan_machine_paths(memory_md))
    findings.extend(check_topic_files(topics_dir))
    findings.extend(check_topic_references(memory_md, topics_dir))
    if topics_dir.is_dir():
        for tf in topics_dir.glob("*.md"):
            findings.extend(scan_machine_paths(tf))
    findings.extend(check_project_file_citations(memory_md, project_root))

    for f in findings:
        f.setdefault("where", f.get("location", str(memory_dir)))

    print(json.dumps({
        "target": str(memory_dir),
        "memory_md_present": memory_md.is_file(),
        "topics_count": len(list(topics_dir.glob("*.md"))) if topics_dir.is_dir() else 0,
        "findings": findings,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
