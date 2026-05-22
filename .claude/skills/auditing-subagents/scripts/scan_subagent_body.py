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
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: scan_subagent_body.py <path>"}))
        return 2

    path = Path(sys.argv[1]).resolve()
    if not path.is_file():
        print(json.dumps({"error": f"not a file: {path}"}))
        return 2

    text = path.read_text(encoding="utf-8", errors="replace")
    fm_text, body = split_frontmatter(text)
    fm = parse_simple_yaml_fields(fm_text or "")

    findings: list[dict] = []

    # SA-4: bypassPermissions + dangerous tools
    if fm.get("permissionMode") == "bypassPermissions":
        tools = fm.get("tools", [])
        if isinstance(tools, str):
            tools_list = [t.strip() for t in tools.split(",")]
        else:
            tools_list = tools
        dangerous_in_tools = []
        for t in tools_list:
            name = re.split(r"\(", t)[0].strip()
            if name in DANGEROUS_TOOLS_FOR_BYPASS:
                dangerous_in_tools.append(t)
        if dangerous_in_tools:
            findings.append({
                "dimension": 6, "severity": "BLOCKER",
                "is_security_critical": True,
                "location": str(path),
                "where": str(path),
                "what": f"`permissionMode: bypassPermissions` combined with dangerous tools {dangerous_in_tools}. (SA-4)",
                "fix": "Remove bypassPermissions, or remove the dangerous tools. Never combine these.",
            })

    # D-5 (T011): negation-aware bypass-approval check.
    # The SUB-BYPASS-PROMPT pattern fires on phrases like "skip the permission policy"
    # — but a phrase preceded by negation ("you do NOT skip the permission policy")
    # is the OPPOSITE intent and should not fire. Python regex doesn't support
    # variable-length lookbehind, so we use a two-pass approach: find candidate
    # matches, then check the preceding window for negation phrases.
    NEGATION_PRE_PATTERN = re.compile(
        r"\b(?:do\s+not|don'?t|never|will\s+not|won'?t|must\s+not|"
        r"mustn'?t|cannot|can'?t|shall\s+not|shan'?t|no\s+matter|"
        r"under\s+no\s+circumstances)\b",
        re.I,
    )
    NEGATION_LOOKBACK_CHARS = 50  # window before match start

    # Pattern scan of body
    body_lines = body.split("\n")
    for pid, pattern, sev, what, fix, is_critical in PATTERNS:
        for i, line in enumerate(body_lines, start=1):
            m = pattern.search(line)
            if not m:
                continue

            # Two-pass: for the negation-sensitive bypass pattern, check the
            # window preceding the match for any negation phrase.
            if pid == "SUB-BYPASS-PROMPT":
                window_start = max(0, m.start() - NEGATION_LOOKBACK_CHARS)
                preceding = line[window_start:m.start()]
                # Also include the previous line's tail in case the negation spans
                # sentence boundaries within the same paragraph.
                if i > 1:
                    prev_line = body_lines[i - 2]
                    preceding = prev_line[-NEGATION_LOOKBACK_CHARS:] + " " + preceding
                if NEGATION_PRE_PATTERN.search(preceding):
                    continue  # negated → suppress finding

            findings.append({
                "dimension": 6, "severity": sev,
                "is_security_critical": is_critical,
                "pattern_id": pid,
                "location": f"{path}:{i + len(fm_text.split(chr(10))) + 2}",  # approximate line in original file
                "where": f"{path}:{i + len(fm_text.split(chr(10))) + 2}",
                "what": what,
                "fix": fix,
            })

    print(json.dumps({
        "target": str(path),
        "findings": findings,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
