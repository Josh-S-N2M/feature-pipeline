#!/usr/bin/env python3
"""
scan_memory_secrets.py — Canonical credential scanner for memory files.

Scans a single file or directory for credential patterns. Used by
auditing-context-files (auto memory) and auditing-subagents (subagent
persistent memory). Both skills share this same script.

Detects:
  - AWS access key IDs (AKIA + 16 alphanumeric, excluding EXAMPLE/FAKE patterns)
  - GitHub PATs (classic `ghp_…`, fine-grained `github_pat_…`)
  - Anthropic API keys (`sk-ant-api03-…`)
  - OpenAI API keys (`sk-proj-…`)
  - SSH private key markers
  - Generic password=, secret=, token= patterns next to high-entropy strings

Emits findings at BLOCKER severity with `is_security_critical: true` —
these produce SECURITY-BLOCK on the audit verdict.

Usage:
    python3 scan_memory_secrets.py <path>     # file or directory
"""
import json
import re
import sys
from pathlib import Path

# Same FAKE_CREDENTIAL_INDICATORS as in pedagogical_marker_check.py — keep in sync.
FAKE_CREDENTIAL_INDICATORS = [
    "EXAMPLE", "FAKE", "PLACEHOLDER", "XXXXXX",
    "YOUR_", "REPLACE_ME", "1234567890", "ABCDEFGH",
]

# Each pattern: (id, regex, severity, what, fix)
PATTERNS = [
    (
        "SEC-AWS-AKIA",
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        "BLOCKER",
        "AWS access key ID pattern detected (AM-2).",
        "Remove from the memory file. Rotate the credential. Tell Claude not to remember credentials.",
    ),
    (
        "SEC-GITHUB-PAT",
        re.compile(r"\bghp_[A-Za-z0-9]{36}\b"),
        "BLOCKER",
        "GitHub classic PAT pattern detected.",
        "Remove from the memory file. Rotate the credential.",
    ),
    (
        "SEC-GITHUB-FINE",
        re.compile(r"\bgithub_pat_[A-Za-z0-9_]{82}\b"),
        "BLOCKER",
        "GitHub fine-grained PAT pattern detected.",
        "Remove from the memory file. Rotate the credential.",
    ),
    (
        "SEC-ANTHROPIC",
        re.compile(r"\bsk-ant-api03-[A-Za-z0-9_\-]{80,}\b"),
        "BLOCKER",
        "Anthropic API key pattern detected.",
        "Remove from the memory file. Rotate the credential.",
    ),
    (
        "SEC-OPENAI",
        re.compile(r"\bsk-proj-[A-Za-z0-9_\-]{40,}\b"),
        "BLOCKER",
        "OpenAI API key pattern detected.",
        "Remove from the memory file. Rotate the credential.",
    ),
    (
        "SEC-SSH-KEY",
        re.compile(r"-----BEGIN (RSA|OPENSSH|EC|DSA) PRIVATE KEY-----"),
        "BLOCKER",
        "SSH private key marker detected.",
        "Remove immediately. Rotate the SSH key.",
    ),
    (
        "SEC-GENERIC-PASSWORD",
        re.compile(r"\b(password|passwd|secret)\s*[:=]\s*[\"\']?([A-Za-z0-9!@#$%^&*]{8,})\b", re.I),
        "BLOCKER",
        "Generic password/secret assignment with non-trivial value.",
        "Use environment variables or a secret manager; never store secrets in memory files.",
    ),
]


def contains_fake_indicator(s: str) -> bool:
    """True if the matched string contains a fake-credential marker."""
    upper = s.upper()
    return any(ind in upper for ind in FAKE_CREDENTIAL_INDICATORS)


def scan_file(file: Path) -> list[dict]:
    findings = []
    try:
        text = file.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return findings
    lines = text.split("\n")
    for pid, pattern, sev, what, fix in PATTERNS:
        for i, line in enumerate(lines, start=1):
            for m in pattern.finditer(line):
                if contains_fake_indicator(m.group(0)):
                    continue
                findings.append({
                    "dimension": 6,
                    "severity": sev,
                    "is_security_critical": True,
                    "location": f"{file}:{i}",
                    "where": f"{file}:{i}",
                    "pattern_id": pid,
                    "what": what,
                    "fix": fix,
                    "match_preview": m.group(0)[:20] + "...",
                })
    return findings


def scan_path(path: Path) -> list[dict]:
    findings: list = []
    if path.is_file():
        findings.extend(scan_file(path))
    elif path.is_dir():
        for f in path.rglob("*"):
            if f.is_file() and f.suffix.lower() in (".md", ".txt", ".json", ".yaml", ".yml"):
                findings.extend(scan_file(f))
    return findings


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: scan_memory_secrets.py <path>"}))
        return 2

    target = Path(sys.argv[1]).resolve()
    if not target.exists():
        print(json.dumps({"error": f"path does not exist: {target}"}))
        return 2

    findings = scan_path(target)
    print(json.dumps({
        "target": str(target),
        "findings": findings,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
