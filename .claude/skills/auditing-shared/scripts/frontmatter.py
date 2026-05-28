"""
frontmatter.py — Shared YAML frontmatter parser for the audit subsystem.

Before this module, four independent implementations of split_frontmatter
existed across auditing-skills, auditing-subagents, auditing-settings, and
auditing-shared. Each was a near-identical copy. Touching one (e.g., to
support a new escape sequence in YAML strings) required editing 4 files.

This module provides one canonical implementation, used by all consumers.

Public surface
--------------

  split_frontmatter(text) -> (fm_text, body_text)
    Split a markdown file's leading `---`-delimited frontmatter from its body.
    Returns (None, original_text) if no valid frontmatter is found.

  parse_simple_yaml_fields(fm_text) -> dict
    Parse a frontmatter block as a flat dict. Handles:
      - key: value (string, int, bool)
      - key: [a, b, c] (flow-style list)
      - key: >- / |  (block scalar continuations)
      - Nested dicts are NOT supported (matches the original simple-YAML scope).
    For full YAML, use PyYAML directly; this is a deliberately limited subset.

  parse_frontmatter(text) -> (dict, body_start_line) | None
    Combines split + parse, returns parsed dict and the line index where the
    body starts (for line-accurate finding emission).
"""

from __future__ import annotations

import re

try:
    import yaml as _yaml  # PyYAML; available in the project's runtime
except Exception:  # pragma: no cover
    _yaml = None


def split_frontmatter(text: str) -> tuple[str | None, str]:
    """Return (frontmatter_text, body_text). Frontmatter is None if missing/malformed."""
    if not text.startswith("---"):
        return None, text
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, text
    # Find the closing `---` line
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            fm_text = "\n".join(lines[1:i])
            body = "\n".join(lines[i + 1 :])
            return fm_text, body
    return None, text


def parse_simple_yaml_fields(fm_text: str) -> dict:
    """Parse a flat-shape YAML frontmatter into a dict.

    Prefers PyYAML if available (the project's runtime has it); falls back to
    a small line-by-line parser for environments where PyYAML is unavailable.
    """
    if _yaml is not None:
        try:
            parsed = _yaml.safe_load(fm_text)
            if isinstance(parsed, dict):
                return parsed
            return {}
        except Exception:
            return {}

    # Fallback: minimal line-by-line parser for environments without PyYAML.
    result: dict = {}
    current_key: str | None = None
    current_list: list | None = None
    for raw_line in fm_text.split("\n"):
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        # List continuation
        if current_list is not None and line.lstrip().startswith("- "):
            current_list.append(line.lstrip()[2:].strip().strip("\"'"))
            continue
        # New key
        m = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", line)
        if not m:
            continue
        if current_list is not None and current_key is not None:
            result[current_key] = current_list
            current_list = None
        key, val = m.group(1), m.group(2).strip()
        if val == "":
            # Block-style list expected next
            current_key = key
            current_list = []
            continue
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            if not inner:
                result[key] = []
            else:
                result[key] = [item.strip().strip("\"'") for item in inner.split(",")]
            current_list = None
            current_key = None
            continue
        if val.lower() in {"true", "false"}:
            result[key] = val.lower() == "true"
        elif val.isdigit():
            result[key] = int(val)
        else:
            result[key] = val.strip("\"'")
        current_key = key
        current_list = None
    if current_list is not None and current_key is not None:
        result[current_key] = current_list
    return result


def parse_frontmatter(text: str) -> tuple[dict, int] | None:
    """Convenience wrapper: split + parse. Returns None if no frontmatter."""
    fm_text, _body = split_frontmatter(text)
    if fm_text is None:
        return None
    fm = parse_simple_yaml_fields(fm_text)
    # Count fm lines including the two `---` delimiters
    body_start = fm_text.count("\n") + 2 + 1  # opening + closing + first body line
    return fm, body_start


if __name__ == "__main__":
    # Self-test
    sample = """---
name: example
description: A test fixture
tools:
  - Read
  - Write
allowed-tools: [Glob, Grep]
---

Body content goes here.
"""
    fm_text, body = split_frontmatter(sample)
    assert fm_text is not None, "split failed"
    assert "name: example" in fm_text, "fm content wrong"
    parsed = parse_simple_yaml_fields(fm_text)
    assert parsed.get("name") == "example", f"name parse failed: {parsed}"
    assert parsed.get("allowed-tools") == ["Glob", "Grep"], f"list parse failed: {parsed}"
    print(f"Self-test PASS: {parsed}")
