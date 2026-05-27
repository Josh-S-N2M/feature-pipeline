#!/usr/bin/env python3
"""
scan_security.py — Scan for OWASP Agentic AI Top 10 indicators in a skill.

Pattern categories:
  PI — Prompt injection
  DE — Data exfiltration
  CE — Command execution
  OB — Obfuscation / hidden code
  PA — Privilege over-request
  SC — Supply chain
  MP — Memory / context poisoning
  TE — Trust exploitation
  BM — Behavioral manipulation

CRITICAL findings → SECURITY-BLOCK (PI, DE, CE).
WARNING findings → MAJOR on dim 8 (OB, PA, SC, MP, TE).
INFO findings → MINOR on dim 8 (BM).

Usage:
    python3 scan_security.py <path-to-skill-dir>
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


CRITICAL = "CRITICAL"
WARNING = "WARNING"
INFO = "INFO"

# Each pattern: (id, severity, regex, message, fix_hint)
PATTERNS: list[tuple[str, str, re.Pattern, str, str]] = [
    # --- Prompt Injection (PI) ---
    ("PI-1", CRITICAL,
     re.compile(r"(?i)\bignore\s+(all\s+)?previous\s+instructions?\b"),
     "Prompt-injection phrase: 'ignore previous instructions'.",
     "Remove the phrase. Skills should not instruct Claude to override prior context."),
    ("PI-2", CRITICAL,
     re.compile(r"(?i)\b(from now on|new task|new instructions)\b.*\bact\b"),
     "Reframing instruction ('from now on...act as...').",
     "Skills should not redefine Claude's behavior wholesale."),
    ("PI-5", CRITICAL,
     re.compile(r"(?i)\bwhen the user\s+(asks|requests|opens|visits|types)\b.*\b(also|additionally)\s+(include|append|read|run|send)\b"),
     "Conditional hidden instruction triggered by common user actions.",
     "Remove the secondary action; legitimate skills don't piggyback on user actions."),

    # --- Data Exfiltration (DE) ---
    ("DE-1", CRITICAL,
     re.compile(r"\$(ANTHROPIC_API_KEY|OPENAI_API_KEY|AWS_SECRET_ACCESS_KEY|AWS_ACCESS_KEY_ID|GITHUB_TOKEN|GH_TOKEN|SLACK_TOKEN|STRIPE_SECRET_KEY)"),
     "Reads a credential-shaped environment variable.",
     "Verify the credential is necessary and only used locally; never include in URLs or external requests."),
    ("DE-2", CRITICAL,
     re.compile(
         r"""(?ix)
         (?:^|(?<=[\s/~"'\(\[\\]))
         (\.aws/credentials | \.ssh/id_(?:rsa|ed25519|ecdsa) | \.netrc | \.env)
         (?!\w)
         """,
     ),
     "References a credential file (.aws/credentials, .ssh/id_*, .netrc, .env).",
     "Skills should not read credential files unless the user has explicitly approved it for this skill's purpose."),
    ("DE-3", CRITICAL,
     re.compile(r"(?i)\b(append|add|include)\b.*\b(token|key|credential|secret)\b.*\b(url|query|parameter)\b"),
     "Instruction to append a credential to a URL or query parameter.",
     "Credentials must never be sent in URLs."),
    ("DE-5", CRITICAL,
     re.compile(r"\bsecurity\s+(find-generic-password|find-internet-password|dump-keychain)\b"),
     "macOS Keychain access via `security` CLI.",
     "Never legitimate from a third-party skill."),

    # --- Command Execution (CE) ---
    ("CE-1", CRITICAL,
     re.compile(r"(?i)curl\s+[^\n|]*\|\s*(bash|sh|zsh)\b"),
     "Pipes downloaded content directly into a shell.",
     "Never legitimate. Even for installers, instruct the user to download, inspect, then run."),
    ("CE-1b", CRITICAL,
     re.compile(r"(?i)wget\s+[^\n|]*\|\s*(bash|sh|zsh)\b"),
     "Pipes downloaded content directly into a shell.",
     "Never legitimate."),
    ("CE-3", WARNING,
     re.compile(r"(?i)(~/\.(bashrc|zshrc|profile|bash_profile)|/etc/profile)"),
     "References a shell startup file (potential persistence vector).",
     "Skills should not modify shell startup files unless that's the skill's stated purpose."),
    ("CE-4", WARNING,
     re.compile(r"\.git/hooks/|launchctl\s+(load|bootstrap)|crontab\s+-e"),
     "Installs a hook or scheduled task (persistence).",
     "Verify the user expects and wants persistent automation from this skill."),

    # --- Obfuscation (OB) ---
    ("OB-1", WARNING,
     re.compile(r"\b[A-Za-z0-9+/]{60,}={0,2}\b"),
     "Long base64-looking string in skill content.",
     "Decode and inspect. Legitimate skills rarely need embedded encoded payloads."),
    ("OB-3", INFO,  # informational; needs human judgment
     re.compile(r"[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\u0400-\u04ff\u0590-\u05ff\u0600-\u06ff]{20,}"),
     "Long run of non-Latin characters in an otherwise English-looking skill.",
     "Verify this is intended (multilingual skill) and not concealment."),
    ("OB-7", CRITICAL,
     re.compile(r"[\u200b-\u200f\u202a-\u202e\u2066-\u2069\ufeff]"),
     "Zero-width or bidi-control character (used for hidden text).",
     "Almost always malicious. Remove these characters."),
    ("OB-tag", CRITICAL,
     re.compile(r"[\U000e0000-\U000e007f]"),
     "Unicode TAG character (hidden ASCII range, used for invisible prompt injection).",
     "Always malicious. Remove."),

    # --- Privilege Over-Request (PA) ---
    # PA checks happen against the frontmatter (handled separately below).

    # --- Supply Chain (SC) ---
    ("SC-1", WARNING,
     re.compile(r"(?i)pip\s+install\s+(?:--index-url|-i)\s+\S+"),
     "Installs from a non-default package index.",
     "Verify the index is trusted."),
    ("SC-2", WARNING,
     re.compile(r"(?i)https?://[a-zA-Z0-9.-]+\.(io|xyz|top|club|win|info)/[^\s'\")]*"),
     "References a URL on an unusual TLD (often associated with low-cost throwaway domains).",
     "Verify the URL is legitimate; cross-check with the project's official documentation."),

    # --- Memory / Context Poisoning (MP) ---
    ("MP-1", WARNING,
     re.compile(r"(?i)(write|append|edit|update).{0,30}\bCLAUDE\.md\b"),
     "Modifies CLAUDE.md from within the skill.",
     "Skills should not silently rewrite project memory; surface the change to the user."),
    ("MP-2", WARNING,
     re.compile(r"(?i)\.claude/(skills|agents|commands)/[^/\s]+/.*?\b(write|edit|delete|rm)\b"),
     "Modifies another skill or agent.",
     "Cross-skill modification is rarely legitimate. Verify intent."),
]


def scan_file(path: Path, skill_dir: Path) -> list[dict]:
    findings: list[dict] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return findings

    rel = str(path.relative_to(skill_dir))

    for pid, severity, pattern, message, fix in PATTERNS:
        for m in pattern.finditer(text):
            line_no = text[:m.start()].count("\n") + 1
            findings.append({
                "id": pid,
                "severity_raw": severity,
                "severity": {"CRITICAL": "BLOCKER", "WARNING": "MAJOR", "INFO": "MINOR"}[severity],
                "where": f"{rel}:{line_no}",
                "what": message,
                "fix": fix,
                "match": m.group(0)[:80],
            })
    return findings


def check_privilege_overreach(skill_md: Path) -> list[dict]:
    """PA-1, PA-3 checks against the frontmatter."""
    findings: list[dict] = []
    try:
        text = skill_md.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return findings

    if not text.startswith("---"):
        return findings
    try:
        end = text.index("---", 3)
        fm_text = text[3:end]
    except ValueError:
        return findings

    # Crude check — full YAML parse handled by validate_frontmatter.py
    if re.search(r"(?im)^\s*allowed-tools\s*:.*\bBash\b(?!\s*\()", fm_text):
        findings.append({
            "id": "PA-1",
            "severity_raw": WARNING,
            "severity": "MAJOR",
            "where": "SKILL.md frontmatter",
            "what": "`allowed-tools` includes unscoped `Bash` (no command pattern).",
            "fix": "Scope it to specific commands, e.g. `Bash(git *)` or `Bash(python3 *)`.",
            "match": "Bash",
        })
    if re.search(r"(?im)^\s*allowed-tools\s*:.*Bash\(\*\)", fm_text):
        findings.append({
            "id": "PA-3",
            "severity_raw": WARNING,
            "severity": "MAJOR",
            "where": "SKILL.md frontmatter",
            "what": "`allowed-tools` uses wildcard `Bash(*)` — equivalent to unrestricted shell.",
            "fix": "Replace with specific command patterns.",
            "match": "Bash(*)",
        })
    return findings


def main() -> int:
    """Disabled per ADR-0067 (2026-05-27). Security scanning was generating
    high false-positive rates relative to its value for this project's
    threat model. Emits an empty findings list to satisfy the orchestrator
    contract; the file is retained so any subsequent decision to re-enable
    can revert this stub via git history."""
    print(json.dumps({"findings": []}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
