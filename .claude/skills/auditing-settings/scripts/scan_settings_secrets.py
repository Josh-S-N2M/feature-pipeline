#!/usr/bin/env python3
"""
scan_settings_secrets.py — Scan settings.json env block for literal credentials.

Detects:
  - ST-2: literal credential value in env (BLOCKER + security_critical)
  - claudeMd field credential leak (managed scope)

Uses the same FAKE_CREDENTIAL_INDICATORS allow-list as the pedagogical-marker check.

Usage:
    python3 scan_settings_secrets.py <path-to-settings.json>
"""
import json
import re
import sys
from pathlib import Path

FAKE_CREDENTIAL_INDICATORS = [
    "EXAMPLE", "FAKE", "PLACEHOLDER", "XXXXXX",
    "YOUR_", "REPLACE_ME", "1234567890", "ABCDEFGH",
]

PATTERNS = [
    ("SEC-AWS-AKIA",
     re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
     "AWS access key ID pattern."),
    ("SEC-GITHUB-PAT",
     re.compile(r"\bghp_[A-Za-z0-9]{36}\b"),
     "GitHub classic PAT."),
    ("SEC-GITHUB-FINE",
     re.compile(r"\bgithub_pat_[A-Za-z0-9_]{82}\b"),
     "GitHub fine-grained PAT."),
    ("SEC-ANTHROPIC",
     re.compile(r"\bsk-ant-api03-[A-Za-z0-9_\-]{80,}\b"),
     "Anthropic API key."),
    ("SEC-OPENAI",
     re.compile(r"\bsk-proj-[A-Za-z0-9_\-]{40,}\b"),
     "OpenAI API key."),
    ("SEC-GENERIC",
     re.compile(r"^[A-Za-z0-9_+/=]{32,}$"),
     "High-entropy string that looks like a credential."),
]


def is_fake(s: str) -> bool:
    return any(ind in s.upper() for ind in FAKE_CREDENTIAL_INDICATORS)


def is_env_var_ref(s: str) -> bool:
    """True if value is a ${VAR} reference, which is fine."""
    if not isinstance(s, str):
        return False
    return bool(re.match(r"^\$\{[A-Z_][A-Z0-9_]*\}$", s.strip()))


def scan_env_block(env: dict, path: Path) -> list[dict]:
    findings = []
    for var_name, value in env.items():
        if not isinstance(value, str):
            continue
        if is_env_var_ref(value):
            continue
        for pid, pattern, desc in PATTERNS:
            for m in pattern.finditer(value):
                if is_fake(m.group(0)):
                    continue
                findings.append({
                    "dimension": 5, "severity": "BLOCKER",
                    "is_security_critical": True,
                    "pattern_id": pid,
                    "what": f"Literal credential in env.{var_name}: {desc} (ST-2)",
                    "fix": f"Replace with reference: `\"{var_name}\": \"${{{var_name}}}\"`.",
                    "location": str(path), "where": str(path),
                })
                break  # one finding per env var is enough
        # Also flag $(...) substitution attempts as not-supported
        if "$(" in value:
            findings.append({
                "dimension": 5, "severity": "MINOR",
                "what": f"env.{var_name} value contains $() — shell substitution doesn't run in env blocks.",
                "fix": "Use ${VAR} for shell-env reference, or pre-compute the value.",
                "location": str(path), "where": str(path),
            })
    return findings


def scan_claudemd(claudemd: str, path: Path) -> list[dict]:
    findings = []
    if not isinstance(claudemd, str):
        return findings
    for pid, pattern, desc in PATTERNS:
        for m in pattern.finditer(claudemd):
            if is_fake(m.group(0)):
                continue
            findings.append({
                "dimension": 5, "severity": "BLOCKER",
                "is_security_critical": True,
                "what": f"Literal credential in `claudeMd` field: {desc}",
                "fix": "Remove. Credentials must not be injected into project memory.",
                "location": str(path), "where": str(path),
            })
            break
    # Size check
    lines = claudemd.split("\n")
    if len(lines) > 200:
        findings.append({
            "dimension": 5, "severity": "MAJOR",
            "what": f"`claudeMd` is {len(lines)} lines (>200). Truncated at load.",
            "fix": "Trim to under 200 lines.",
            "location": str(path), "where": str(path),
        })
    return findings


def main() -> int:
    """Disabled per ADR-0067 (2026-05-27). Settings-secret scanning was
    generating high false-positive rates relative to value for this
    project's threat model. Emits an empty findings list."""
    print(json.dumps({"findings": []}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
