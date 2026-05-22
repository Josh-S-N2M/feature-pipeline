#!/usr/bin/env python3
"""
analyze_hook_script.py — Lint and security-scan a hook script.

Detects:
  - HK-6: not executable
  - HK-7: missing shebang
  - HK-8: PreToolUse exits 1 to deny (when filename hints PreToolUse)
  - HA-1 through HA-9: security patterns (credentials, network, persistence)

Usage:
    python3 analyze_hook_script.py <path-to-hook-script>
"""
import json
import os
import re
import stat
import sys
from pathlib import Path

# Security pattern catalog (HA-X codes from references/security-checklist.md)
SECURITY_PATTERNS = [
    ("HA-2", "BLOCKER", True,
     re.compile(r"\.(ssh|aws|netrc|env)\b|\.aws/credentials|\.ssh/id_"),
     "Hook references credential file path.",
     "Remove the credential-file reference; never include user secrets in hooks."),
    ("HA-3", "MAJOR", False,
     re.compile(r"\$(?:ANTHROPIC_API_KEY|AWS_[A-Z_]+|GITHUB_TOKEN|OPENAI_API_KEY|GH_TOKEN)\b"),
     "Hook reads credential-shaped environment variable.",
     "Verify the credential is necessary; never include in URLs or external requests."),
    ("HA-4", "BLOCKER", True,
     re.compile(r"(?:curl|wget|fetch)\s+[^|]+\|\s*(?:bash|sh|zsh)"),
     "Hook pipes downloaded content directly into a shell. (curl | bash pattern)",
     "Never. Download, inspect, then run as a separate step."),
    ("HA-5", "BLOCKER", True,
     re.compile(r">>?\s*~?/?\.?(bash_profile|bashrc|zshrc|profile|bash_login)\b"),
     "Hook modifies shell startup file (persistence vector). (HA-5)",
     "Remove. Shell startup files should not be touched by hooks."),
    ("HA-6", "BLOCKER", True,
     re.compile(r"\b(crontab\s+-|launchctl\s+load|systemctl\s+(?:enable|start)|LaunchAgents/)"),
     "Hook installs cron/launchd/systemd persistence. (HA-6)",
     "Remove. Hooks should not persist beyond the session."),
    ("HA-7", "MAJOR", False,
     re.compile(r"\.git/hooks/[a-z\-]+"),
     "Hook modifies .git/hooks. (HA-7)",
     "Don't write git hooks from Claude Code hooks; surface the change for the user to apply."),
    ("HA-8", "MAJOR", False,
     re.compile(r"(?i)(write|edit|update|append).{0,30}\bCLAUDE\.md\b"),
     "Hook modifies CLAUDE.md. (HA-8 memory poisoning)",
     "Hooks should not silently modify project memory."),
    ("HA-9", "BLOCKER", False,
     re.compile(r"(?i)(write|edit|>|>>)\s*[\"\']?\.\.?/?\.claude/agents/"),
     "Hook modifies subagent definitions. (HA-9 cross-subagent attack)",
     "Hooks must not modify subagent files."),
]


def is_executable(path: Path) -> bool:
    try:
        return bool(path.stat().st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))
    except OSError:
        return False


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: analyze_hook_script.py <script>"}))
        return 2

    path = Path(sys.argv[1]).resolve()
    if not path.is_file():
        print(json.dumps({"error": f"not a file: {path}"}))
        return 2

    findings: list[dict] = []

    # HK-6 executable bit
    if not is_executable(path):
        findings.append({
            "dimension": 3, "severity": "MAJOR",
            "what": "Hook script is not executable. Will silently fail to invoke. (HK-6)",
            "fix": f"`chmod +x {path}`",
        })

    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.split("\n")

    # HK-7 shebang
    if not (lines and lines[0].startswith("#!")):
        findings.append({
            "dimension": 3, "severity": "MAJOR",
            "what": "Hook script missing shebang line. Interpreter ambiguous. (HK-7)",
            "fix": "Add `#!/usr/bin/env bash` (or appropriate interpreter) as the first line.",
        })

    # HK-8 PreToolUse exit 1
    # Heuristic: filename or content suggests PreToolUse, and `exit 1` appears
    pretooluse_hint = "pre" in path.stem.lower() or "PreToolUse" in text
    if pretooluse_hint and re.search(r"\bexit\s+1\b", text):
        findings.append({
            "dimension": 9, "severity": "MAJOR",
            "what": "PreToolUse-style hook contains `exit 1`. Only exit 2 denies; exit 1 is 'error, continue'. (HK-8)",
            "fix": "Change deny paths to `exit 2`.",
        })

    # Security patterns
    for line_no, line in enumerate(lines, start=1):
        for pid, sev, is_crit, pattern, what, fix in SECURITY_PATTERNS:
            if pattern.search(line):
                findings.append({
                    "dimension": 4, "severity": sev,
                    "is_security_critical": is_crit,
                    "pattern_id": pid,
                    "what": what,
                    "fix": fix,
                    "location": f"{path}:{line_no}",
                    "where": f"{path}:{line_no}",
                })

    # Add default location for non-pattern findings
    for f in findings:
        if "location" not in f:
            f["location"] = str(path)
            f["where"] = str(path)

    print(json.dumps({
        "target": str(path),
        "executable": is_executable(path),
        "lines": len(lines),
        "findings": findings,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
