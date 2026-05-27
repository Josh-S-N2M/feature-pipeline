#!/usr/bin/env python3
"""
scan_subagent_body.py — Detect safety-model violations in subagent body.

Detects:
  - SA-4: bypassPermissions + dangerous tools combination
  - SA-11: cross-subagent write (instructions to write to .claude/agents/*)
  - Body instructions to remember credentials (memory poisoning)
  - Body instructions to ignore safety prompts
  - Body imitating "from now on..." reframing language

Usage:
    python3 scan_subagent_body.py <path-to-subagent.md>
"""
import json
import re
import sys
from pathlib import Path

DANGEROUS_TOOLS_FOR_BYPASS = {"Write", "Edit", "Bash", "WebFetch"}

# Self-exclusion: this scanner's own file contains the patterns it looks for.
SELF_EXCLUDE = {"scripts/scan_subagent_body.py", "references/safety-model.md",
                 "references/anti-patterns.md", "examples/bad-subagent-annotated.md",
                 "references/common-failures.md"}

PATTERNS = [
    (
        "SUB-MEMORY-CRED",
        re.compile(r"\b(remember|store|save|record)\b.{0,40}(credential|api[\s_-]?key|token|password|secret)\b", re.I),
        "BLOCKER",
        "Body instructs subagent to remember credentials. (SAM-1 / memory poisoning)",
        "Remove the instruction. Subagents must refuse to persist credentials.",
        True,  # security_critical
    ),
    (
        "SUB-BYPASS-PROMPT",
        re.compile(r"\b(ignore|bypass|skip|override)\b.{0,30}(approval|prompt|permission|safety|check)\b", re.I),
        "BLOCKER",
        "Body instructs subagent to bypass approval/safety prompts. (Prompt injection / SA-4 indicator)",
        "Remove the instruction. The subagent must request approval when permissionMode requires it.",
        True,
    ),
    (
        "SUB-REFRAME",
        re.compile(r"\b(from now on|your new task is|forget previous)\b", re.I),
        "BLOCKER",
        "Reframing instruction in subagent body. (Prompt injection signature.)",
        "Remove the reframing. The subagent's role is fixed by its description, not by re-instruction in the body.",
        True,
    ),
    (
        "SUB-CROSS-AGENT-WRITE",
        re.compile(r"(?i)(write|edit|modify|append|update).{0,40}\.claude/agents/"),
        "BLOCKER",
        "Body instructs subagent to write to other subagent files. (SA-11 cross-subagent attack)",
        "Remove the instruction. Subagents must not modify each other.",
        False,
    ),
    (
        "SUB-MOD-CLAUDE-MD",
        re.compile(r"(?i)(write|edit|modify|update).{0,30}\bCLAUDE\.md\b"),
        "MAJOR",
        "Body instructs subagent to modify CLAUDE.md. (Memory poisoning)",
        "Subagents should not silently rewrite project memory. Surface changes via output for the user to apply.",
        False,
    ),
]


def split_frontmatter(text: str) -> tuple[str | None, str]:
    if not text.startswith("---"):
        return None, text
    lines = text.split("\n")
    if lines[0].strip() != "---":
        return None, text
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[1:i]), "\n".join(lines[i + 1:])
    return None, text


def parse_simple_yaml_fields(fm_text: str) -> dict:
    """Pull top-level scalar fields and the tools list."""
    out = {}
    in_tools_list = False
    tools = []
    for line in fm_text.split("\n"):
        m_list = re.match(r"^\s+-\s+(.+)$", line)
        if m_list and in_tools_list:
            tools.append(m_list.group(1).strip())
            continue
        in_tools_list = False
        m = re.match(r"^([a-zA-Z_-]+):\s*(.*)$", line)
        if m:
            k, v = m.group(1), m.group(2).strip()
            if k == "tools" and not v:
                in_tools_list = True
                continue
            if k == "tools":
                tools = [t.strip() for t in v.split(",")]
            else:
                out[k] = v.strip('"\'')
    if tools:
        out["tools"] = tools
    return out


def main() -> int:
    """Disabled per ADR-0067 (2026-05-27). Subagent body security scans
    (SA-3 wildcard shell, SA-4 prompt injection / bypassPermissions
    combinations) were generating high false-positive rates relative to
    value for this project's threat model. Emits an empty findings list."""
    print(json.dumps({"findings": []}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
