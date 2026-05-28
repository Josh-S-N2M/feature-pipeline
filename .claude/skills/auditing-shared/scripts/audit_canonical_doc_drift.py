#!/usr/bin/env python3
"""
audit_canonical_doc_drift.py — CANON-2 document-level canonical drift.

CANON-1 (audit_canonical_drift.py) catches Python audit scripts that redefine
a canonical constant. CANON-2 catches *documents* (markdown) that hard-code a
canonical vocabulary inline instead of referencing its canonical source.

The motivating case: the engineering-domain-layers vocabulary lived only in
markdown prose and was duplicated verbatim across the PRD template, Blueprint
template, and KB-documentation-criteria SKILL.md before it was migrated into
.claude/canonical/engineering-domain-layers.yaml (ADR-0069). CANON-2 prevents
that duplication from creeping back.

How it decides
--------------
For each watched vocabulary, a document "hard-codes" it when the document
contains at least `min_match` of the vocabulary's canonical member strings.

- The canonical source file and the declared prose companion are EXEMPT — they
  are *supposed* to enumerate the vocabulary.
- A document that contains the enumeration AND also references the canonical
  source path is downgraded to INFO ("derived view with a pointer back to
  canonical" — acceptable, mirrors CANON-1's import-alias exemption). The
  design-composer's layer→KB mapping table and the templates are this case.
- A document that enumerates without any reference is a MAJOR drift finding.

Historical / immutable trees are excluded from scanning (working/, Issues/,
adrs/, output/, agent-memory) — they are point-in-time records, not live
config the drift rule governs.

Usage:
    python3 audit_canonical_doc_drift.py <repo-root>
Exits 0 always; emits {"rule": "CANON-2", "findings": [...]} on stdout.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def _find_repo_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / ".claude" / "canonical").is_dir():
            return p
    raise RuntimeError(f"Could not find repo root from {start}")


# Directories whose contents are point-in-time records, not live config.
EXCLUDED_DIR_PARTS = {
    ".git", "working", "Issues", "adrs", "output", "node_modules",
    "agent-memory", "agent-memory-local",
}

# Generated artifacts — regenerated each run; not a drift surface.
EXCLUDED_FILENAMES = {
    "project-audit-report.md",
    "pipeline-validation-analysis.md",
}


def _is_excluded(path: Path, repo: Path) -> bool:
    rel_parts = set(path.relative_to(repo).parts)
    if rel_parts & EXCLUDED_DIR_PARTS:
        return True
    return path.name in EXCLUDED_FILENAMES


def _watched_vocabularies(repo: Path) -> list[dict]:
    """Build the watched-vocabulary list from canonical data.

    Thresholds are tuned to 'near-complete enumeration' so the rule fires on
    documents that essentially redefine a whole vocabulary (specs, templates,
    rubrics, the owning audit skill) — not on teaching docs that mention a few
    members in prose.
    """
    _shared = repo / ".claude" / "skills" / "auditing-shared" / "scripts"
    sys.path.insert(0, str(_shared))
    from canonical import layers, severity, doc_types, hook_events  # noqa: E402

    # issue_states: drop the bare-`wontfix` legacy alias from the match set so
    # the substring 'wontfix' inside 'wontfix-with-rationale' doesn't inflate
    # counts; the 6 distinct lifecycle states are the real signal.
    issue_states = sorted(s for s in doc_types.ISSUE_STATES if s != "wontfix")

    return [
        {
            "name": "engineering-domain-layers",
            "members": layers.NAMES,
            "min_match": 6,  # 6 of 9 names ⇒ almost certainly a full enumeration
            "source": ".claude/canonical/engineering-domain-layers.yaml",
            "prose_companion": ".claude/skills/KB-documentation-criteria/references/layer-taxonomy.md",
            "reference_markers": ["engineering-domain-layers.yaml", "layer-taxonomy.md"],
        },
        {
            "name": "severity",
            "members": severity.ORDER,            # 5 members
            "min_match": 5,                       # all 5 ⇒ full enumeration
            "source": ".claude/canonical/severity.yaml",
            "prose_companion": ".claude/skills/KB-review-disciplines/references/severity-taxonomy.md",
            "reference_markers": ["severity.yaml"],
        },
        {
            "name": "issue-states",
            "members": issue_states,              # 6 distinct lifecycle states
            "min_match": 6,                       # all 6 ⇒ full enumeration
            "source": ".claude/canonical/doc-types.yaml",
            "prose_companion": ".claude/skills/KB-documentation-criteria/references/issue-doctypes-spec.md",
            "reference_markers": ["doc-types.yaml"],
        },
        {
            "name": "hook-events",
            "members": sorted(hook_events.VALID_EVENTS),  # 13 members
            "min_match": 9,                       # 9+ ⇒ substantial enumeration
            "source": ".claude/canonical/hook-events.yaml",
            "prose_companion": ".claude/skills/auditing-hooks/references/hook-spec.md",
            "reference_markers": ["hook-events.yaml"],
        },
        {
            "name": "gated-doc-types",
            "members": sorted(doc_types.GATED_DOC_TYPES),  # 13 members
            "min_match": 9,                       # 9+ ⇒ substantial enumeration
            "source": ".claude/canonical/doc-types.yaml",
            "prose_companion": ".claude/skills/KB-documentation-criteria/references/shared-conventions.md",
            "reference_markers": ["doc-types.yaml"],
        },
    ]


def main() -> int:
    if len(sys.argv) < 2:
        repo = _find_repo_root(Path(__file__).resolve())
    else:
        repo = Path(sys.argv[1]).resolve()

    vocabularies = _watched_vocabularies(repo)
    findings: list[dict] = []

    # Scan markdown under .claude/ plus root-level AGENTS.md / *.md.
    candidates: list[Path] = []
    candidates.extend((repo / ".claude").rglob("*.md"))
    candidates.extend(repo.glob("*.md"))

    seen_real: set[str] = set()
    for doc in sorted(candidates):
        if _is_excluded(doc, repo):
            continue
        real = str(doc.resolve())  # dedup symlinks (CLAUDE.md -> AGENTS.md)
        if real in seen_real:
            continue
        seen_real.add(real)

        text = doc.read_text(encoding="utf-8", errors="replace")
        rel = doc.relative_to(repo).as_posix()

        for vocab in vocabularies:
            # Exempt the canonical source + prose companion.
            if rel in (vocab["source"], vocab["prose_companion"]):
                continue

            matched = [m for m in vocab["members"] if m in text]
            if len(matched) < vocab["min_match"]:
                continue

            has_reference = any(mk in text for mk in vocab["reference_markers"])
            if has_reference:
                findings.append({
                    "rule": "CANON-2",
                    "severity": "INFO",
                    "what": (
                        f"{rel} enumerates {len(matched)}/{len(vocab['members'])} "
                        f"members of the canonical '{vocab['name']}' vocabulary but "
                        f"references the canonical source — treated as a derived view."
                    ),
                    "fix": (
                        f"OK as a derived/functional view because it points back to "
                        f"{vocab['source']}. Keep the reference; do not let the inline "
                        f"list drift from canonical."
                    ),
                    "location": rel,
                    "where": rel,
                    "dimension": 1,
                })
            else:
                findings.append({
                    "rule": "CANON-2",
                    "severity": "MAJOR",
                    "what": (
                        f"{rel} hard-codes {len(matched)}/{len(vocab['members'])} "
                        f"members of the canonical '{vocab['name']}' vocabulary inline "
                        f"with NO reference to the canonical source. This is a drift "
                        f"surface — the inline list can fall out of sync with "
                        f"{vocab['source']}."
                    ),
                    "fix": (
                        f"Replace the inline enumeration with a reference to "
                        f"{vocab['source']} (or its prose companion "
                        f"{vocab['prose_companion']}). If an inline list is genuinely "
                        f"needed (e.g. a functional mapping table), add an explicit "
                        f"pointer to the canonical source so this rule treats it as a "
                        f"derived view."
                    ),
                    "location": rel,
                    "where": rel,
                    "dimension": 1,
                })

    print(json.dumps({"rule": "CANON-2", "findings": findings}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
