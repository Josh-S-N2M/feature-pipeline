#!/usr/bin/env python3
"""
audit_op8_gitnexus.py — OP-8 GitNexus install + probe consumer check.

Verifies:
  1. .devcontainer/versions.env declares GITNEXUS_TAG.
  2. .mcp.json gitnexus entry uses `npx -y gitnexus@${GITNEXUS_TAG} mcp` (per cycle-3 F2).
  3. .mcp.json gitnexus entry sets env GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1 (per AC-CS-9).
  4. .devcontainer/postCreate.sh exports GITNEXUS_SKIP_OPTIONAL_GRAMMARS BEFORE `npm install -g gitnexus`.
  5. discovery-codebase-researcher + review-architecture-auditor agents both
     carry `mcp__gitnexus__*` in their allowlists.

Usage:
    python3 audit_op8_gitnexus.py <repo-root>
"""
import json
import re
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: audit_op8_gitnexus.py <repo-root>"}))
        return 2

    repo = Path(sys.argv[1]).resolve()
    findings = []

    # 1. versions.env has GITNEXUS_TAG
    versions = repo / ".devcontainer" / "versions.env"
    if not versions.exists():
        findings.append({"rule": "OP-8", "severity": "BLOCKER", "message": "versions.env missing"})
    elif "GITNEXUS_TAG" not in versions.read_text():
        findings.append({"rule": "OP-8", "severity": "BLOCKER", "message": "GITNEXUS_TAG not declared in versions.env"})

    # 2 + 3. .mcp.json gitnexus entry
    mcp_json = repo / ".mcp.json"
    if mcp_json.exists():
        cfg = json.loads(mcp_json.read_text())
        gx = cfg.get("mcpServers", {}).get("gitnexus", {})
        if not gx:
            findings.append({"rule": "OP-8", "severity": "BLOCKER", "message": ".mcp.json: gitnexus entry missing"})
        else:
            if gx.get("command") != "npx":
                findings.append({"rule": "OP-8", "severity": "BLOCKER",
                                 "message": f".mcp.json: gitnexus command should be 'npx' (cycle-3 F2); got {gx.get('command')!r}"})
            args = gx.get("args", [])
            if "gitnexus@${GITNEXUS_TAG}" not in " ".join(args):
                findings.append({"rule": "OP-8", "severity": "MAJOR",
                                 "message": ".mcp.json: gitnexus args missing 'gitnexus@${GITNEXUS_TAG}' (cycle-3 F2)"})
            env = gx.get("env", {})
            if env.get("GITNEXUS_SKIP_OPTIONAL_GRAMMARS") != "1":
                findings.append({"rule": "OP-8", "severity": "BLOCKER",
                                 "message": ".mcp.json: gitnexus env missing GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1 (AC-CS-9 wrapping intent)"})
    else:
        findings.append({"rule": "OP-8", "severity": "BLOCKER", "message": ".mcp.json missing"})

    # 4. postCreate.sh exports env-var
    pc = repo / ".devcontainer" / "postCreate.sh"
    if pc.exists():
        text = pc.read_text()
        # Look for: export GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1 ... npm install -g gitnexus
        export_pos = text.find("export GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1")
        install_pos = text.find("npm install -g \"gitnexus")
        # Match either single-quoted or unquoted
        if install_pos == -1:
            install_pos = text.find("npm install -g gitnexus")
        if export_pos == -1 or install_pos == -1:
            findings.append({"rule": "OP-8", "severity": "MAJOR",
                             "message": "postCreate.sh: missing export GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1 OR `npm install -g gitnexus`"})
        elif export_pos > install_pos:
            findings.append({"rule": "OP-8", "severity": "BLOCKER",
                             "message": "postCreate.sh: export GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1 appears AFTER `npm install -g gitnexus` (AC-CS-9 requires before)"})

    # 5. Consumer agents carry mcp__gitnexus__*
    for agent in ("discovery-codebase-researcher", "review-architecture-auditor"):
        ap = repo / ".claude" / "agents" / f"{agent}.md"
        if not ap.exists():
            findings.append({"rule": "OP-8", "severity": "BLOCKER", "agent": agent, "message": "agent file missing"})
            continue
        head = "\n".join(ap.read_text().splitlines()[:20])
        if "mcp__gitnexus__*" not in head:
            findings.append({"rule": "OP-8", "severity": "MAJOR", "agent": agent,
                             "message": "agent missing mcp__gitnexus__* in tools allowlist"})

    out = {
        "rule": "OP-8",
        "name": "GitNexus install + probe consumers",
        "findings": findings,
    }
    print(json.dumps(out, indent=2))
    return 1 if any(f["severity"] == "BLOCKER" for f in findings) else (2 if findings else 0)


if __name__ == "__main__":
    sys.exit(main())
