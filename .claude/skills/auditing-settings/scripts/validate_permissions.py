#!/usr/bin/env python3
"""
validate_permissions.py — Validate the `permissions` block of settings.json.

Detects:
  - ST-3: Permissive Bash allow
  - ST-4: Missing deny-baseline items (especially in --managed mode)
  - ST-7: WebFetch with no scoping
  - ST-9: Bare tool name (no parens)
  - ST-10: Same pattern in allow and deny
  - Invalid permission rule syntax (literal quotes, etc.)

Usage:
    python3 validate_permissions.py <path-to-settings.json> [--managed]
"""
import json
import re
import sys
from pathlib import Path

# Bootstrap import of the canonical accessor (single source of truth for
# tool inventory, severity vocabulary, naming patterns, etc.). See
# .claude/canonical/README.md and ADR-0068.
_here = Path(__file__).resolve()
for _p in _here.parents:
    if (_p / ".claude" / "canonical").is_dir():
        sys.path.insert(0, str(_p / ".claude" / "skills" / "auditing-shared" / "scripts"))
        break
from canonical import tools as _tools  # noqa: E402

# Tool name supports letters, digits, underscores, hyphens, and `*` so MCP
# tool patterns (`mcp__<server>__*`, `mcp__<server>__<tool_name>`) and any
# future tool naming that uses these characters validate cleanly.
RULE_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_\-*]*)(?:\((.+)\))?$")

# Deny baseline patterns the auditor expects to find in --managed mode
DENY_BASELINE = [
    "Bash(rm -rf /",
    "Bash(rm -rf ~",
    "Bash(curl",
    "Bash(wget",
    "Bash(eval",
    "Write(/etc",
    "Write(~/.ssh",
    "WebFetch(file:",
]


def parse_rule(rule: str) -> tuple[str | None, str | None]:
    """Return (tool, scope) or (None, None) if unparseable."""
    m = RULE_RE.match(rule.strip())
    if not m:
        return None, None
    return m.group(1), m.group(2)


def check_rule_syntax(rule: str, list_name: str, location: str) -> list[dict]:
    findings = []
    tool, scope = parse_rule(rule)
    if tool is None:
        findings.append({
            "dimension": 3, "severity": "MAJOR",
            "what": f"Permission rule '{rule}' (in '{list_name}') has unrecognized syntax.",
            "fix": "Use `Tool(pattern)` format. See permission-rules-spec.md.",
            "location": location, "where": location,
        })
        return findings

    # MCP tool patterns (`mcp__<server>__<tool>`, `mcp__<server>__*`) are
    # generated per registered MCP server and aren't in the static known-tools
    # set. They're valid Claude Code permission patterns; skip the
    # unknown-tool check for them.
    is_mcp_tool = tool.startswith(_tools.MCP_TOOL_PREFIX)

    if not is_mcp_tool and tool not in _tools.KNOWN_TOOLS:
        findings.append({
            "dimension": 3, "severity": "MINOR",
            "what": f"Permission rule references unknown tool '{tool}' (in '{list_name}').",
            "fix": "Check spelling. Known: " + ", ".join(sorted(_tools.KNOWN_TOOLS)),
            "location": location, "where": location,
        })

    # ST-9: bare tool name (no parens)
    if scope is None and tool in _tools.BARE_EQUIVALENT_TO_WILDCARD:
        findings.append({
            "dimension": 3, "severity": "MAJOR",
            "what": f"Bare tool name '{tool}' in '{list_name}' is equivalent to '{tool}(*)'. (ST-9)",
            "fix": f"Add scoping: '{tool}(<pattern>)'.",
            "location": location, "where": location,
        })

    # Literal quotes inside parens
    if scope and ('"' in scope or "'" in scope):
        findings.append({
            "dimension": 3, "severity": "MAJOR",
            "what": f"Permission rule '{rule}' has quote characters inside parens. The quotes are part of the literal pattern; the rule won't match real tool calls.",
            "fix": "Remove the inner quotes.",
            "location": location, "where": location,
        })

    return findings


def check_permissive_allow(allow_list: list, location: str, managed: bool) -> list[dict]:
    """ST-3 / ST-7 permissive-allow check.

    Disabled in non-managed mode per ADR-0067 follow-on (2026-05-27): the
    permissive-allow finding has a circular relationship with ST-9 (bare tool
    name) — fixing ST-9 by adding explicit `(*)` immediately re-triggers ST-3 /
    ST-7. For a single-developer research project that intentionally grants
    broad Bash and WebFetch access, this finding is workflow noise. The check
    remains active in `--managed` mode (production / multi-tenant policies)
    where broad allow rules are genuinely concerning."""
    findings = []
    if not managed:
        return findings
    permissive_pats = {"Bash(*)", "WebFetch(*)", "Write(**)", "Edit(**)"}
    for rule in allow_list:
        if not isinstance(rule, str):
            continue
        if rule.strip() in permissive_pats:
            findings.append({
                "dimension": 3, "severity": "BLOCKER",
                "what": f"Permissive allow rule '{rule}'. {'(ST-3)' if 'Bash' in rule else '(ST-7)'}",
                "fix": "Scope to specific patterns.",
                "location": location, "where": location,
            })
    return findings


def check_deny_baseline(deny_list: list, location: str, managed: bool) -> list[dict]:
    findings = []
    deny_strs = [r if isinstance(r, str) else "" for r in deny_list]
    if not managed:
        return findings  # baseline check only in --managed mode

    for baseline_prefix in DENY_BASELINE:
        if not any(d.startswith(baseline_prefix) for d in deny_strs):
            findings.append({
                "dimension": 4, "severity": "MINOR",
                "what": f"Managed deny list missing baseline item starting with '{baseline_prefix}...'. (ST-4)",
                "fix": f"Add a deny rule for this pattern. See managed-settings-spec.md for the full baseline.",
                "location": location, "where": location,
            })
    return findings


def check_allow_deny_overlap(allow_list: list, deny_list: list, location: str) -> list[dict]:
    findings = []
    allow_set = {r.strip() for r in allow_list if isinstance(r, str)}
    deny_set = {r.strip() for r in deny_list if isinstance(r, str)}
    overlap = allow_set & deny_set
    for rule in overlap:
        findings.append({
            "dimension": 3, "severity": "MINOR",
            "what": f"Rule '{rule}' appears in both allow and deny. Deny wins; allow is dead config. (ST-10)",
            "fix": "Remove from allow, or remove from deny if it was a typo.",
            "location": location, "where": location,
        })
    return findings


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(json.dumps({"error": "Usage: validate_permissions.py <settings.json> [--managed]"}))
        return 2

    path = Path(args[0]).resolve()
    managed = "--managed" in args

    if not path.is_file():
        print(json.dumps({"error": f"not a file: {path}"}))
        return 2

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(json.dumps({"findings": [], "error": f"JSON parse: {e}"}))
        return 0

    perms = data.get("permissions", {})
    if not isinstance(perms, dict):
        print(json.dumps({"findings": [{
            "dimension": 1, "severity": "MAJOR",
            "what": "`permissions` is not a JSON object.",
            "fix": "Use `permissions: { \"allow\": [...], \"deny\": [...], \"ask\": [...] }`",
            "location": str(path), "where": str(path),
        }]}))
        return 0

    findings: list[dict] = []
    location = str(path)

    for list_name in ("allow", "deny", "ask"):
        rules = perms.get(list_name, [])
        if not isinstance(rules, list):
            findings.append({
                "dimension": 3, "severity": "MAJOR",
                "what": f"`permissions.{list_name}` is not a list.",
                "fix": "Use a JSON list of permission rule strings.",
                "location": location, "where": location,
            })
            continue
        for rule in rules:
            if isinstance(rule, str):
                findings.extend(check_rule_syntax(rule, list_name, location))

    findings.extend(check_permissive_allow(perms.get("allow", []), location, managed))
    findings.extend(check_deny_baseline(perms.get("deny", []), location, managed))
    findings.extend(check_allow_deny_overlap(perms.get("allow", []), perms.get("deny", []), location))

    print(json.dumps({
        "target": str(path),
        "managed_mode": managed,
        "findings": findings,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
