"""
canonical.py — Loader for .claude/canonical/ YAML files (the single source
of truth for shared vocabulary across the audit subsystem and the project
at large).

Every audit script that needs to reference a shared concept (tool names,
hook event names, severity vocabulary, naming patterns, frontmatter fields,
doc-type vocabularies, skill thresholds, audit rule registry) MUST import
from this module rather than defining its own copy. The CANON-1 drift
audit fires on any local redefinition.

Public surface — typed accessors that load + cache + expose the canonical
data as ready-to-use Python objects.

Usage
-----

    from canonical import tools, hook_events, severity, naming, \
        frontmatter_fields, doc_types, skill_thresholds, audit_rules

    if rule not in tools.KNOWN_TOOLS:
        ...

    if event not in hook_events.VALID_EVENTS:
        ...

Resolution
----------

Canonical YAML files live at `<repo-root>/.claude/canonical/*.yaml`.
The loader walks up from `__file__` to find the repo root, then reads
the YAML once per process (cached).

If a canonical file is missing or malformed, the loader raises a clear
exception at first access — better to fail loudly than to silently use
defaults that drift.
"""

from __future__ import annotations

import re
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


# ---------- Filesystem discovery ----------


def _find_repo_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / ".claude" / "canonical").is_dir() and (p / ".git").exists():
            return p
        if (p / ".git").exists() and (p / ".claude").is_dir():
            return p
    raise RuntimeError(f"Could not find repo root from {start}")


_REPO_ROOT = _find_repo_root(Path(__file__).resolve())
_CANONICAL_DIR = _REPO_ROOT / ".claude" / "canonical"


@lru_cache(maxsize=None)
def _load_yaml(name: str) -> dict:
    path = _CANONICAL_DIR / name
    if not path.is_file():
        raise RuntimeError(
            f"Canonical file missing: {path}. "
            f"Either the file was deleted (drift!) or this script is running "
            f"outside the project root."
        )
    try:
        with path.open(encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise RuntimeError(f"Canonical file {path} is malformed: {e}") from e


# ---------- tools.yaml ----------


class _Tools:
    @property
    def _data(self) -> dict:
        return _load_yaml("tools.yaml")

    @property
    def BUILT_IN(self) -> set[str]:
        return set(self._data.get("built_in", []))

    @property
    def MODEL_INVOCABLE(self) -> set[str]:
        return set(self._data.get("model_invocable", []))

    @property
    def KNOWN_TOOLS(self) -> set[str]:
        return self.BUILT_IN | self.MODEL_INVOCABLE

    @property
    def BARE_EQUIVALENT_TO_WILDCARD(self) -> set[str]:
        return set(self._data.get("bare_equivalent_to_wildcard", []))

    @property
    def DANGEROUS_TOOLS(self) -> set[str]:
        return set(self._data.get("dangerous_tools", []))

    @property
    def MCP_TOOL_PATTERN(self) -> re.Pattern[str]:
        pat = self._data.get("mcp_tool_pattern", {}).get("pattern", "")
        return re.compile(pat)

    @property
    def MCP_TOOL_PREFIX(self) -> str:
        return self._data.get("mcp_tool_pattern", {}).get("prefix", "mcp__")


tools = _Tools()


# ---------- hook-events.yaml ----------


class _HookEvents:
    @property
    def _data(self) -> dict:
        return _load_yaml("hook-events.yaml")

    @property
    def VALID_EVENTS(self) -> set[str]:
        return {e["name"] for e in self._data.get("events", [])}

    @property
    def CONTEXT_VARIABLES(self) -> list[str]:
        return [v["name"] for v in self._data.get("context_variables", [])]

    def expand_path(self, command: str, project_root: Path) -> str:
        """Expand documented hook-context variables in a command string."""
        from os.path import expanduser

        result = command
        if "${CLAUDE_PROJECT_DIR}" in result:
            result = result.replace("${CLAUDE_PROJECT_DIR}", str(project_root))
        if "${HOME}" in result:
            result = result.replace("${HOME}", expanduser("~"))
        return result


hook_events = _HookEvents()


# ---------- severity.yaml ----------


class _Severity:
    @property
    def _data(self) -> dict:
        return _load_yaml("severity.yaml")

    @property
    def ORDER(self) -> list[str]:
        return list(self._data.get("order", []))

    @property
    def SCORE_WEIGHTS(self) -> dict[str, float]:
        return {
            name: meta.get("score_weight", 0)
            for name, meta in self._data.get("severities", {}).items()
        }

    @property
    def ORDINALS(self) -> dict[str, int]:
        return {
            name: meta.get("ordinal", 99)
            for name, meta in self._data.get("severities", {}).items()
        }

    @property
    def VERDICT_BANDS(self) -> list[tuple[float, str]]:
        return [
            (b.get("threshold", 0), b.get("verdict", "FAIL"))
            for b in self._data.get("verdict_bands", [])
        ]

    def verdict_from_score(self, score: float) -> str:
        for threshold, verdict in self.VERDICT_BANDS:
            if score >= threshold:
                return verdict
        return "FAIL"


severity = _Severity()


# ---------- naming.yaml ----------


class _Naming:
    @property
    def _data(self) -> dict:
        return _load_yaml("naming.yaml")

    @property
    def SKILL_NAME_PATTERN(self) -> re.Pattern[str]:
        return re.compile(self._data.get("skill_name", {}).get("pattern", "^.+$"))

    @property
    def SUBAGENT_NAME_PATTERN(self) -> re.Pattern[str]:
        return re.compile(
            self._data.get("subagent_name", {}).get("pattern", "^.+$")
        )

    @property
    def RESERVED_WORDS(self) -> set[str]:
        # Union of reserved words across both primitive types
        skill_reserved = set(self._data.get("skill_name", {}).get("reserved_words", []))
        sub_reserved = set(self._data.get("subagent_name", {}).get("reserved_words", []))
        return skill_reserved | sub_reserved

    @property
    def NAME_MAX_LENGTH(self) -> int:
        return self._data.get("skill_name", {}).get("max_length", 64)

    @property
    def XML_INJECTION_PATTERN(self) -> re.Pattern[str]:
        meta = self._data.get("xml_injection_pattern", {})
        flags = 0
        if meta.get("flags", "").upper() == "IGNORECASE":
            flags = re.IGNORECASE
        return re.compile(meta.get("pattern", "<script"), flags)

    @property
    def SKILL_NAMESPACE_PREFIXES(self) -> list[str]:
        return [n["prefix"] for n in self._data.get("skill_namespaces", [])]


naming = _Naming()


# ---------- frontmatter-fields.yaml ----------


class _FrontmatterFields:
    @property
    def _data(self) -> dict:
        return _load_yaml("frontmatter-fields.yaml")

    @property
    def SKILL_RECOGNIZED(self) -> set[str]:
        return set(self._data.get("skill", {}).get("recognized", []))

    @property
    def SUBAGENT_RECOGNIZED(self) -> set[str]:
        return set(self._data.get("subagent", {}).get("recognized", []))

    @property
    def SLASH_COMMAND_RECOGNIZED(self) -> set[str]:
        return set(self._data.get("slash_command", {}).get("recognized", []))

    @property
    def PIPELINE_DOC_RECOGNIZED(self) -> set[str]:
        return set(self._data.get("pipeline_doc_recognized", []))


frontmatter_fields = _FrontmatterFields()


# ---------- doc-types.yaml ----------


class _DocTypes:
    @property
    def _data(self) -> dict:
        return _load_yaml("doc-types.yaml")

    @property
    def GATED_DOC_TYPES(self) -> set[str]:
        return set(self._data.get("gated_doc_types", []))

    @property
    def GATED_STATES(self) -> set[str]:
        return set(self._data.get("gated_states", []))

    @property
    def ANALYSIS_DOC_TYPES(self) -> set[str]:
        return set(self._data.get("analysis_doc_types", []))

    @property
    def ANALYSIS_STATES(self) -> set[str]:
        return set(self._data.get("analysis_states", []))

    @property
    def ADR_STATES(self) -> set[str]:
        return set(self._data.get("adr_states", []))

    @property
    def ISSUE_DOC_TYPES(self) -> set[str]:
        return set(self._data.get("issue_doc_types", []))

    @property
    def ISSUE_STATES(self) -> set[str]:
        return set(self._data.get("issue_states", []))

    @property
    def ISSUE_PER_STATE_REQUIRED_FIELDS(self) -> dict[str, list[str]]:
        return dict(self._data.get("issue_per_state_required_fields", {}))

    @property
    def EFFORT_ENUM(self) -> set[str]:
        return set(self._data.get("effort_levels", []))


doc_types = _DocTypes()


# ---------- skill-thresholds.yaml ----------


class _SkillThresholds:
    @property
    def _data(self) -> dict:
        return _load_yaml("skill-thresholds.yaml")

    def line_thresholds_for(self, skill_name: str) -> tuple[int, int]:
        """Return (major_threshold, blocker_threshold) for a skill name."""
        rules = self._data.get("skill_md_line_thresholds", {})
        # Try prefix matches first (KB-, recipe-)
        for prefix, cfg in rules.items():
            if prefix == "default":
                continue
            if skill_name.startswith(prefix):
                return cfg.get("major", 500), cfg.get("blocker", 1000)
        default = rules.get("default", {})
        return default.get("major", 500), default.get("blocker", 1000)

    @property
    def TOC_REQUIRED_ABOVE_LINES(self) -> int:
        return self._data.get("reference_file_thresholds", {}).get(
            "toc_required_above_lines", 100
        )

    @property
    def IMPLICIT_DIRECTORIES(self) -> set[str]:
        return set(self._data.get("implicit_directories", []))

    @property
    def IMPLICIT_FILE_SUFFIXES(self) -> set[str]:
        return set(self._data.get("implicit_file_suffixes", []))

    @property
    def DESCRIPTION_MAX_CHARS(self) -> int:
        return self._data.get("description_field", {}).get("warning_chars", 1024)

    @property
    def DESCRIPTION_PLUS_WHEN_TO_USE_MAX(self) -> int:
        return self._data.get("description_field", {}).get(
            "combined_with_when_to_use_max", 1536
        )


skill_thresholds = _SkillThresholds()


# ---------- audit-rules.yaml ----------


class _AuditRules:
    @property
    def _data(self) -> dict:
        return _load_yaml("audit-rules.yaml")

    @property
    def RULES(self) -> list[dict[str, Any]]:
        return list(self._data.get("rules", []))

    @property
    def DISABLED_RULES(self) -> list[dict[str, Any]]:
        return [r for r in self.RULES if r.get("status") == "disabled"]

    @property
    def ACTIVE_RULES(self) -> list[dict[str, Any]]:
        return [r for r in self.RULES if r.get("status") == "active"]

    @property
    def REMOVED_RULES(self) -> list[dict[str, Any]]:
        return [r for r in self.RULES if r.get("status") == "removed"]

    def lookup(self, rule_id: str) -> dict[str, Any] | None:
        for r in self.RULES:
            if r.get("id") == rule_id:
                return r
        return None

    def is_disabled(self, rule_id: str) -> bool:
        r = self.lookup(rule_id)
        return r is not None and r.get("status") == "disabled"

    def is_active(self, rule_id: str) -> bool:
        r = self.lookup(rule_id)
        return r is not None and r.get("status") == "active"

    @property
    def DRIFT_DETECTION_WATCHED_NAMES(self) -> set[str]:
        return set(
            self._data.get("drift_detection_rule", {}).get(
                "watched_constant_names", []
            )
        )


audit_rules = _AuditRules()


# ---------- engineering-domain-layers.yaml ----------


class _Layers:
    @property
    def _data(self) -> dict:
        return _load_yaml("engineering-domain-layers.yaml")

    @property
    def ORDER(self) -> list[str]:
        """Canonical layer slugs in load-bearing order."""
        return list(self._data.get("order", []))

    @property
    def LAYERS(self) -> dict[str, dict]:
        """Slug -> per-layer metadata (name, short, design_kbs, platform_kbs, …)."""
        return dict(self._data.get("layers", {}))

    @property
    def NAMES(self) -> list[str]:
        """Canonical display names, in order."""
        layers = self.LAYERS
        return [layers[slug]["name"] for slug in self.ORDER if slug in layers]

    @property
    def NAME_SET(self) -> set[str]:
        return set(self.NAMES)

    @property
    def SLUGS(self) -> set[str]:
        return set(self.LAYERS.keys())

    def name_for(self, slug: str) -> str:
        return self.LAYERS.get(slug, {}).get("name", slug)

    def design_kbs_for(self, slug: str) -> list[str]:
        return list(self.LAYERS.get(slug, {}).get("design_kbs", []))

    def platform_kbs_for(self, slug: str) -> list[str]:
        return list(self.LAYERS.get(slug, {}).get("platform_kbs", []))

    @property
    def CHECKBOX_BLOCK(self) -> str:
        """The verbatim Layer Scope checkbox block, generated from canonical
        data so the PRD/Blueprint never hand-maintain the list."""
        lines = []
        layers = self.LAYERS
        for slug in self.ORDER:
            meta = layers.get(slug, {})
            lines.append(f"- [ ] **{meta.get('name', slug)}** — {meta.get('short', '')}")
        return "\n".join(lines)


layers = _Layers()


# ---------- CLI smoke (lets `python3 canonical.py` self-test the loader) ----------


def _smoke() -> int:
    print(f"Canonical dir: {_CANONICAL_DIR}")
    print(f"  tools.KNOWN_TOOLS: {len(tools.KNOWN_TOOLS)} entries")
    print(f"  hook_events.VALID_EVENTS: {len(hook_events.VALID_EVENTS)} entries")
    print(f"  severity.ORDER: {severity.ORDER}")
    print(f"  naming.SKILL_NAME_PATTERN: {naming.SKILL_NAME_PATTERN.pattern}")
    print(
        f"  frontmatter_fields.SKILL_RECOGNIZED: {len(frontmatter_fields.SKILL_RECOGNIZED)} fields"
    )
    print(f"  doc_types.ISSUE_DOC_TYPES: {doc_types.ISSUE_DOC_TYPES}")
    print(
        f"  skill_thresholds.line_thresholds_for('KB-foo'): {skill_thresholds.line_thresholds_for('KB-foo')}"
    )
    print(f"  audit_rules.ACTIVE_RULES: {len(audit_rules.ACTIVE_RULES)}")
    print(f"  audit_rules.DISABLED_RULES: {len(audit_rules.DISABLED_RULES)}")
    print(f"  audit_rules.REMOVED_RULES: {len(audit_rules.REMOVED_RULES)}")
    print(f"  layers.NAMES: {layers.NAMES}")
    return 0


if __name__ == "__main__":
    sys.exit(_smoke())
