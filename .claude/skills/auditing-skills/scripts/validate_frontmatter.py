#!/usr/bin/env python3
"""
validate_frontmatter.py — Validate YAML frontmatter against the canonical spec.

Checks:
  - Frontmatter is present and parseable.
  - name (if present): <=64 chars, lowercase+digits+hyphens, no XML, no reserved words.
  - description (if present): <=1024 chars, non-empty, no XML.
  - description + when_to_use combined <=1536 chars.
  - No tab characters in the frontmatter block.
  - Field names that look like skill-vs-agent confusion (`tools:` instead of `allowed-tools:`).
  - Recognized fields only (warn on unrecognized).

Usage:
    python3 validate_frontmatter.py <path-to-SKILL.md>
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print(json.dumps({
        "error": "PyYAML not installed. Run: pip install pyyaml",
        "findings": [],
    }))
    sys.exit(0)


# Bootstrap canonical accessor (single source of truth for names, fields, patterns).
_here = Path(__file__).resolve()
for _p in _here.parents:
    if (_p / ".claude" / "canonical").is_dir():
        sys.path.insert(0, str(_p / ".claude" / "skills" / "auditing-shared" / "scripts"))
        break
from canonical import naming as _naming, frontmatter_fields as _ff  # noqa: E402

RECOGNIZED_FIELDS = _ff.SKILL_RECOGNIZED
NAME_PATTERN = _naming.SKILL_NAME_PATTERN
RESERVED_NAME_WORDS = tuple(_naming.RESERVED_WORDS)
XML_TAG_PATTERN = _naming.XML_INJECTION_PATTERN


def split_frontmatter(text: str) -> tuple[str | None, str]:
    """Forwarder to the canonical split_frontmatter in auditing-shared/.
    Single source of truth per ADR-0068."""
    from frontmatter import split_frontmatter as _shared
    return _shared(text)  # No closing ---


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: validate_frontmatter.py <SKILL.md>", "findings": []}))
        return 2

    import os
    target_type = os.environ.get("AUDIT_TARGET_TYPE", "skill")  # "skill" or "slash-command"

    path = Path(sys.argv[1])
    if not path.is_file():
        print(json.dumps({"error": f"not a file: {path}", "findings": []}))
        return 2

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="replace")

    findings: list[dict] = []

    # Check for BOM
    if text.startswith("\ufeff"):
        findings.append({
            "severity": "BLOCKER",
            "what": "File starts with a UTF-8 BOM. The frontmatter `---` must be the very first bytes.",
            "fix": "Re-save the file as UTF-8 without BOM.",
        })
        text = text.lstrip("\ufeff")

    # Check for leading whitespace before ---
    if not text.startswith("---") and text.lstrip().startswith("---"):
        findings.append({
            "severity": "BLOCKER",
            "what": "There is whitespace before the opening `---` of the frontmatter.",
            "fix": "Remove leading whitespace; `---` must be the first three characters.",
        })

    fm_text, _body = split_frontmatter(text)

    if fm_text is None:
        findings.append({
            "severity": "BLOCKER",
            "what": "Frontmatter not found or missing closing `---`. The skill will be silently dropped.",
            "fix": "Ensure SKILL.md starts with `---`, has YAML, and ends the block with `---` on its own line.",
        })
        print(json.dumps({"findings": findings, "frontmatter": None}))
        return 0

    # Tab detection in frontmatter
    if "\t" in fm_text:
        findings.append({
            "severity": "BLOCKER",
            "what": "Frontmatter contains tab characters. YAML requires spaces only.",
            "fix": "Replace all tabs in the frontmatter block with spaces.",
        })

    # Try to parse
    try:
        fm = yaml.safe_load(fm_text)
    except yaml.YAMLError as e:
        findings.append({
            "severity": "BLOCKER",
            "what": f"Frontmatter failed to parse as YAML: {e}",
            "fix": "Fix the YAML syntax. Common causes: unquoted colons in values, missing quotes around special chars.",
        })
        print(json.dumps({"findings": findings, "frontmatter": None}))
        return 0

    if not isinstance(fm, dict):
        findings.append({
            "severity": "BLOCKER",
            "what": "Frontmatter parsed but is not a mapping (key:value structure).",
            "fix": "Frontmatter must be a YAML mapping with fields like `name:` and `description:`.",
        })
        print(json.dumps({"findings": findings, "frontmatter": None}))
        return 0

    # Field-name confusion: skills use allowed-tools, agents use tools
    if "tools" in fm and "allowed-tools" not in fm:
        findings.append({
            "severity": "BLOCKER",
            "what": "Field `tools:` is used. Skills use `allowed-tools:`; `tools:` is the agent format and is silently ignored here.",
            "fix": "Rename `tools:` to `allowed-tools:`. (See claude-code issue #27099.)",
        })

    # Description checks
    desc = fm.get("description")
    if desc is None:
        findings.append({
            "severity": "MAJOR",
            "what": "No `description` field. Without it, Claude relies on the first body paragraph (fragile).",
            "fix": "Add a `description:` field that says what the skill does and when to use it.",
        })
    else:
        if not isinstance(desc, str):
            findings.append({
                "severity": "BLOCKER",
                "what": "`description` is not a string.",
                "fix": "Make `description:` a string value.",
            })
        else:
            desc_str = desc.strip()
            if not desc_str:
                findings.append({
                    "severity": "BLOCKER",
                    "what": "`description` is empty.",
                    "fix": "Add a description that says what the skill does and when to use it.",
                })
            if len(desc_str) > 1024:
                findings.append({
                    "severity": "BLOCKER",
                    "what": f"`description` is {len(desc_str)} chars (max 1024).",
                    "fix": "Shorten the description.",
                })
            if XML_TAG_PATTERN.search(desc_str):
                findings.append({
                    "severity": "BLOCKER",
                    "what": "`description` contains XML-style tags, which are not allowed.",
                    "fix": "Remove any `<...>` tags from the description.",
                })

    # Combined description + when_to_use cap
    when = fm.get("when_to_use", "")
    if isinstance(when, str) and isinstance(desc, str):
        combined = len(desc) + len(when)
        if combined > 1536:
            findings.append({
                "severity": "MAJOR",
                "what": f"description + when_to_use is {combined} chars (>1536). Tail will be truncated in the skill listing.",
                "fix": "Trim either field so the combined length is under 1536.",
            })

    # Name checks
    name = fm.get("name")
    if name is not None:
        if not isinstance(name, str):
            findings.append({
                "severity": "BLOCKER",
                "what": "`name` is not a string.",
                "fix": "Make `name:` a string value.",
            })
        else:
            if len(name) > 64:
                findings.append({
                    "severity": "BLOCKER",
                    "what": f"`name` is {len(name)} chars (max 64).",
                    "fix": "Shorten the name.",
                })
            if not NAME_PATTERN.match(name):
                findings.append({
                    "severity": "BLOCKER",
                    "what": f"`name` ({name!r}) contains characters other than lowercase letters, digits, and hyphens.",
                    "fix": "Use only lowercase letters, digits, and hyphens.",
                })
            if XML_TAG_PATTERN.search(name):
                findings.append({
                    "severity": "BLOCKER",
                    "what": "`name` contains XML-style tags.",
                    "fix": "Remove any `<...>` tags from the name.",
                })
            for word in RESERVED_NAME_WORDS:
                if word in name.lower():
                    findings.append({
                        "severity": "BLOCKER",
                        "what": f"`name` contains the reserved word {word!r}.",
                        "fix": f"Pick a name that doesn't include {word!r}.",
                    })

    # Unrecognized fields (MINOR — they're silently ignored, which is a footgun)
    unrecognized = [k for k in fm if k not in RECOGNIZED_FIELDS and k != "tools"]
    if unrecognized:
        findings.append({
            "severity": "MINOR",
            "what": f"Unrecognized frontmatter field(s): {unrecognized}. These are silently ignored.",
            "fix": "Remove them, or check for typos (e.g. `descripton` instead of `description`).",
        })

    print(json.dumps({
        "findings": findings,
        "frontmatter": fm,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
