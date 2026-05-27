#!/usr/bin/env python3
"""audit_feature_touch_coverage.py — SA-14 hard gate for agent-roster impact matrix.

Runs at deliverable packaging time to verify that if the advisory predicate
(check_feature_touch_predicate.py / T5.2) fired for a feature run, the
agent-roster-impact-matrix.md artifact MUST exist in working/feature/<slug>/
and must comply with the ADR-0064 Clause 2 contract (row count, five columns,
positive-evidence-string cell discipline).

This is the HARD GATE that catches missing or malformed matrices at packaging
time, complementing the advisory predicate (T5.2) which is design-time guidance
only.  Unlike the predicate, SA-14 is not advisory — exit 1 means FAIL and
must be resolved before the deliverable is packaged.

References:
  ADR-0064 — Agent-Roster Impact Matrix Contract (Clauses 2, 3)
  FR-10     — pipeline-design-time-discipline-r1 PRD (SA-14 backstop mechanism)
  ADR-0061  — Severity vocabulary bridge (BLOCKER / MAJOR / MINOR / NOTE)
  NFR-8     — Four-field finding shape: rule / target / divergence / next_action

Severity choices per ADR-0061 bridge table:
  BLOCKER — matrix absent when predicate fired; blocks deliverable packaging.
  MAJOR   — matrix present but structurally non-compliant (bad cells / row count).
  (MINOR / NOTE not used by SA-14 — all structural failures are BLOCKER or MAJOR.)

Exit codes:
  0 = PASS (predicate silent, or matrix present and compliant)
  1 = FAIL (findings emitted: matrix missing or structurally non-compliant)
  2 = invocation error (missing args, file not found, JSON parse error)

Output: JSON to stdout, log messages to stderr.
Python 3.8+ stdlib only.

Discipline: add new rule entry, not extend existing (per synthesis D-R2a-5).
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

RULE_MISSING = "SA-14.matrix_missing"
RULE_ROW_COUNT = "SA-14.row_count_mismatch"
RULE_CELL_BARE = "SA-14.cell_bare_no_change"
RULE_TABLE_NOT_FOUND = "SA-14.matrix_table_not_found"
RULE_TABLE_AMBIGUOUS = "SA-14.matrix_table_ambiguous"

MATRIX_FILENAME = "agent-roster-impact-matrix.md"
AGENTS_DIR_GLOB = ".claude/agents/*.md"
TEMPLATE_PATH = (
    ".claude/skills/KB-documentation-criteria/references/templates/"
    "agent-roster-impact-matrix-template.md"
)

# Five explicit dimensions per ADR-0064 Clause 2
REQUIRED_COLUMNS = {"tools", "skills", "model", "effort", "prompt body"}

# Pipe-delimited markdown table: |col1|col2|...| — detect separator rows
_SEPARATOR_ROW_RE = re.compile(r"^\|[\s\-:|]+\|")

# A cell with ONLY "no-change" (case-insensitive, possibly whitespace padded)
# and NO evidence string after a dash/em-dash is structurally insufficient.
# Acceptable forms: "no-change — <evidence>" or "no-change — <evidence>"
# Bare forms: "no-change", " no-change ", " no change "
_BARE_NO_CHANGE_RE = re.compile(
    r"^\s*no[- ]?change\s*$",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Predicate integration
# ---------------------------------------------------------------------------

def _run_predicate(feature_slug: str, repo_root: str) -> Tuple[Optional[Dict], Optional[str]]:
    """Invoke check_feature_touch_predicate.py and return (parsed_json, error_msg).

    Returns the JSON output dict, or (None, error_msg) on failure.
    """
    predicate_path = (
        Path(__file__).parent / "check_feature_touch_predicate.py"
    )
    if not predicate_path.exists():
        return None, f"predicate script not found at: {predicate_path}"

    try:
        result = subprocess.run(
            [
                sys.executable,
                str(predicate_path),
                "--feature-slug", feature_slug,
                "--repo-root", repo_root,
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        return None, "predicate invocation timed out after 60 s"
    except OSError as exc:
        return None, f"failed to invoke predicate: {exc}"

    stdout = result.stdout.strip()
    if not stdout:
        return None, (
            f"predicate produced no stdout (exit {result.returncode}); "
            f"stderr: {result.stderr.strip()[:200]}"
        )

    try:
        data = json.loads(stdout)
    except json.JSONDecodeError as exc:
        return None, f"predicate output is not valid JSON: {exc}"

    return data, None


def _load_predicate_output(
    predicate_json_path: str,
) -> Tuple[Optional[Dict], Optional[str]]:
    """Load predicate output from a pre-existing JSON file."""
    path = Path(predicate_json_path)
    if not path.exists():
        return None, f"predicate output file not found: {predicate_json_path}"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, f"cannot read predicate output: {exc}"
    return data, None


# ---------------------------------------------------------------------------
# Agent-count helper
# ---------------------------------------------------------------------------

def _count_agents(repo_root: str) -> Tuple[int, Optional[str]]:
    """Return (count, error_msg) of .claude/agents/*.md files."""
    agents_dir = Path(repo_root) / ".claude" / "agents"
    if not agents_dir.is_dir():
        return 0, f".claude/agents/ directory not found at {agents_dir}"
    files = [f for f in agents_dir.glob("*.md") if f.is_file()]
    return len(files), None


# ---------------------------------------------------------------------------
# Matrix parsing + validation (ADR-0064 Clause 2)
# ---------------------------------------------------------------------------

def _split_row(row: str) -> List[str]:
    """Strip leading/trailing |, split on |, strip each cell."""
    return [cell.strip() for cell in row.strip("|").split("|")]


def _collect_all_tables(text: str) -> List[Tuple[List[str], List[List[str]]]]:
    """Scan *text* and return ALL pipe-delimited Markdown tables found.

    Each table is represented as (headers, rows).  The scanner accumulates
    consecutive pipe-line blocks; a non-pipe line (blank or otherwise) ends
    the current table and the scanner moves on to the next one.
    """
    lines = text.splitlines()
    tables: List[Tuple[List[str], List[List[str]]]] = []
    current_block: List[str] = []

    def _flush(block: List[str]) -> None:
        if len(block) < 2:
            return
        headers = _split_row(block[0])
        rows = []
        for line in block[1:]:
            if _SEPARATOR_ROW_RE.match(line):
                continue  # skip separator row (|---|---|)
            rows.append(_split_row(line))
        if headers:
            tables.append((headers, rows))

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            current_block.append(stripped)
        else:
            if current_block:
                _flush(current_block)
                current_block = []

    # Flush any trailing table block
    if current_block:
        _flush(current_block)

    return tables


def _is_canonical_matrix_table(headers: List[str]) -> bool:
    """Return True if *headers* contain all five required canonical column names."""
    normalised = {_normalise_header(h) for h in headers}
    return REQUIRED_COLUMNS.issubset(normalised)


def _parse_markdown_table(
    text: str,
) -> Tuple[List[str], List[List[str]], Optional[str]]:
    """Find the canonical 5-column matrix table among all tables in *text*.

    Returns (headers, rows, error_rule) where:
    - On success: (headers, rows, None) — the matching canonical table
    - On no-match: ([], [], RULE_TABLE_NOT_FOUND)
    - On ambiguous: ([], [], RULE_TABLE_AMBIGUOUS)

    Callers that previously expected (headers, rows) must be updated to unpack
    three values and propagate the error_rule when non-None.
    """
    all_tables = _collect_all_tables(text)
    matching = [
        (hdrs, rows)
        for hdrs, rows in all_tables
        if _is_canonical_matrix_table(hdrs)
    ]

    if len(matching) == 0:
        return [], [], RULE_TABLE_NOT_FOUND
    if len(matching) > 1:
        return [], [], RULE_TABLE_AMBIGUOUS

    headers, rows = matching[0]
    return headers, rows, None


def _normalise_header(header: str) -> str:
    """Lower-case and strip markdown bold markers for comparison."""
    return re.sub(r"\*+", "", header).strip().lower()


def _validate_matrix(
    matrix_path: Path,
    agent_count_expected: int,
    feature_slug: str,
) -> Tuple[List[Dict], int]:
    """Validate the matrix per ADR-0064 Clause 2.

    Returns (findings, row_count_observed).
    Findings use NFR-8 four-field shape: rule / target / divergence / next_action / severity.
    """
    findings: List[Dict] = []
    target = str(matrix_path)

    try:
        text = matrix_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        findings.append({
            "rule": RULE_MISSING,
            "target": target,
            "divergence": f"Matrix file unreadable: {exc}",
            "next_action": "Ensure the matrix file is readable and UTF-8 encoded.",
            "severity": "BLOCKER",
        })
        return findings, 0

    headers, rows, table_err = _parse_markdown_table(text)

    if table_err == RULE_TABLE_NOT_FOUND:
        findings.append({
            "rule": RULE_TABLE_NOT_FOUND,
            "target": target,
            "divergence": (
                "No table with all five canonical column headers "
                "(tools, skills, model, effort, prompt body) was found in the matrix "
                "file. The file may contain tables but none matches the required "
                "five-column ADR-0064 Clause 2 shape."
            ),
            "next_action": (
                "Ensure the matrix contains a pipe-delimited Markdown table whose "
                "header row includes all five columns: tools, skills, model, effort, "
                f"prompt body.  Expected {agent_count_expected} data rows."
            ),
            "severity": "BLOCKER",
        })
        return findings, 0

    if table_err == RULE_TABLE_AMBIGUOUS:
        findings.append({
            "rule": RULE_TABLE_AMBIGUOUS,
            "target": target,
            "divergence": (
                "Multiple tables in the matrix file each match the five-column "
                "canonical header signature (tools, skills, model, effort, prompt body). "
                "SA-14 cannot determine which table is authoritative."
            ),
            "next_action": (
                "Ensure the matrix file contains exactly one table whose header row "
                "carries the five ADR-0064 Clause 2 columns. Remove or rename "
                "duplicate header columns in any auxiliary tables."
            ),
            "severity": "MAJOR",
        })
        return findings, 0

    if not headers:
        findings.append({
            "rule": RULE_TABLE_NOT_FOUND,
            "target": target,
            "divergence": (
                "No markdown table found in matrix file — cannot parse rows or columns."
            ),
            "next_action": (
                "Ensure the matrix contains a valid pipe-delimited Markdown table "
                f"with five columns (tools, skills, model, effort, prompt body) "
                f"and {agent_count_expected} data rows."
            ),
            "severity": "BLOCKER",
        })
        return findings, 0

    row_count_observed = len(rows)

    # --- Row count check ---
    if row_count_observed != agent_count_expected:
        findings.append({
            "rule": RULE_ROW_COUNT,
            "target": target,
            "divergence": (
                f"Matrix has {row_count_observed} data row(s) but "
                f"{agent_count_expected} agent file(s) exist at "
                f".claude/agents/*.md — 'evaluated by absence' failure mode "
                "(ADR-0064 Rationale 2)."
            ),
            "next_action": (
                f"Add or remove rows until the matrix has exactly "
                f"{agent_count_expected} rows — one per .claude/agents/*.md file."
            ),
            "severity": "MAJOR",
        })

    # --- Column presence check (five explicit dimensions) ---
    normalised_headers = [_normalise_header(h) for h in headers]
    missing_cols = REQUIRED_COLUMNS - set(normalised_headers)
    if missing_cols:
        findings.append({
            "rule": RULE_ROW_COUNT,
            "target": target,
            "divergence": (
                f"Matrix is missing required column(s): {sorted(missing_cols)}. "
                "ADR-0064 Clause 2 mandates five explicit dimensions: "
                "tools, skills, model, effort, prompt body."
            ),
            "next_action": (
                "Add the missing column(s) to the matrix table header and "
                "populate each agent's cell with <value> — <positive-evidence-string>."
            ),
            "severity": "MAJOR",
        })
        # Cannot check cell discipline without knowing which column is which
        return findings, row_count_observed

    # --- Per-cell positive-evidence-string discipline ---
    # We check all data cells (not just the five known columns) for bare no-change.
    bare_cells: List[Tuple[int, int, str]] = []  # (row_idx, col_idx, cell_value)

    for row_idx, row in enumerate(rows):
        for col_idx, cell in enumerate(row):
            if _BARE_NO_CHANGE_RE.match(cell):
                bare_cells.append((row_idx + 1, col_idx + 1, cell))

    if bare_cells:
        # Emit one MAJOR finding listing the offending cells
        cell_descriptions = [
            f"row {r}, col {c} = {v!r}" for r, c, v in bare_cells[:10]
        ]
        suffix = f" (and {len(bare_cells) - 10} more)" if len(bare_cells) > 10 else ""
        findings.append({
            "rule": RULE_CELL_BARE,
            "target": target,
            "divergence": (
                f"{len(bare_cells)} cell(s) contain bare 'no-change' without a "
                "positive-evidence string — structurally insufficient per "
                "ADR-0064 Clause 2 (bare `no-change` without an evidence string "
                "fails both FR-6 design-time block and FR-10 packaging-time backstop). "
                f"Offending cells: {', '.join(cell_descriptions)}{suffix}."
            ),
            "next_action": (
                "Replace each bare 'no-change' cell with the form "
                "'no-change — <positive-evidence-string>' where the evidence string "
                "is a short rationale derived from inspectable evidence "
                "(the agent's prompt body, tools list, or surrounding context)."
            ),
            "severity": "MAJOR",
        })

    return findings, row_count_observed


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    start = time.monotonic()

    parser = argparse.ArgumentParser(
        description=(
            "SA-14 hard gate: verify the agent-roster-impact-matrix.md exists and "
            "is structurally compliant whenever the advisory predicate fired for "
            "this feature run.  Runs at deliverable packaging time."
        ),
        epilog=(
            "Exit 0 = PASS (not applicable or matrix compliant). "
            "Exit 1 = FAIL (matrix missing or non-compliant). "
            "Exit 2 = invocation error."
        ),
    )
    parser.add_argument(
        "--feature-slug",
        required=True,
        help="Feature slug (e.g. 'pipeline-design-time-discipline-r1').",
    )
    parser.add_argument(
        "--predicate-output",
        default=None,
        help=(
            "Path to a pre-computed check_feature_touch_predicate.py JSON output file. "
            "If omitted, SA-14 invokes the predicate automatically."
        ),
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help=(
            "Explicit repo root path. Defaults to the repository root derived "
            "from the current working directory."
        ),
    )
    args = parser.parse_args()

    cwd = os.getcwd()

    # --- Resolve repo root ---
    if args.repo_root:
        repo_root = str(Path(args.repo_root).resolve())
    else:
        # Try git to find repo root
        try:
            r = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True, text=True, timeout=15, cwd=cwd,
            )
            if r.returncode == 0:
                repo_root = r.stdout.strip()
            else:
                repo_root = cwd
        except (OSError, subprocess.TimeoutExpired):
            repo_root = cwd

    feature_slug = args.feature_slug
    matrix_path = Path(repo_root) / "working" / "feature" / feature_slug / MATRIX_FILENAME

    # --- Step 1: get predicate output ---
    if args.predicate_output:
        predicate_data, pred_err = _load_predicate_output(args.predicate_output)
    else:
        predicate_data, pred_err = _run_predicate(feature_slug, repo_root)

    if predicate_data is None:
        result = {
            "sa14_status": "error",
            "rule": RULE_MISSING,
            "feature_slug": feature_slug,
            "matrix_path": str(matrix_path),
            "agent_count_expected": None,
            "row_count_observed": None,
            "findings": [
                {
                    "rule": RULE_MISSING,
                    "target": str(matrix_path),
                    "divergence": f"Cannot obtain predicate output: {pred_err}",
                    "next_action": (
                        "Ensure check_feature_touch_predicate.py is reachable and "
                        "the feature slug is correct, or supply --predicate-output."
                    ),
                    "severity": "BLOCKER",
                }
            ],
            "verdict": "FAIL",
            "elapsed_ms": int((time.monotonic() - start) * 1000),
        }
        print(json.dumps(result, indent=2))
        return 2

    predicate_fired = predicate_data.get("predicate_fired", False)

    # --- Step 2: not-applicable fast path ---
    if not predicate_fired:
        result = {
            "sa14_status": "not_applicable",
            "rule": RULE_MISSING,
            "feature_slug": feature_slug,
            "matrix_path": str(matrix_path),
            "agent_count_expected": None,
            "row_count_observed": None,
            "findings": [],
            "verdict": "PASS",
            "elapsed_ms": int((time.monotonic() - start) * 1000),
        }
        print(json.dumps(result, indent=2))
        return 0

    # --- Step 3: predicate fired — matrix is required ---
    agent_count_expected, agent_err = _count_agents(repo_root)
    if agent_err:
        print(f"WARNING: {agent_err}", file=sys.stderr)

    # --- Step 4a: matrix missing ---
    if not matrix_path.exists():
        finding = {
            "rule": RULE_MISSING,
            "target": str(matrix_path.relative_to(repo_root) if matrix_path.is_absolute() else matrix_path),
            "divergence": (
                "Predicate fired but agent-roster-impact-matrix.md is absent at "
                "deliverable packaging time (ADR-0064 Clause 2; FR-10)."
            ),
            "next_action": (
                f"Author the matrix from the template at {TEMPLATE_PATH} "
                "per ADR-0064.  Every .claude/agents/*.md agent needs one row with "
                "five cells (tools, skills, model, effort, prompt body), each "
                "containing <value> — <positive-evidence-string>."
            ),
            "severity": "BLOCKER",
        }
        result = {
            "sa14_status": "findings",
            "rule": RULE_MISSING,
            "feature_slug": feature_slug,
            "matrix_path": str(matrix_path),
            "agent_count_expected": agent_count_expected,
            "row_count_observed": None,
            "findings": [finding],
            "verdict": "FAIL",
            "elapsed_ms": int((time.monotonic() - start) * 1000),
        }
        print(json.dumps(result, indent=2))
        return 1

    # --- Step 4b: matrix present — validate per ADR-0064 Clause 2 ---
    findings, row_count_observed = _validate_matrix(
        matrix_path, agent_count_expected, feature_slug
    )

    has_findings = bool(findings)
    sa14_status = "findings" if has_findings else "clean"
    verdict = "FAIL" if has_findings else "PASS"

    result = {
        "sa14_status": sa14_status,
        "feature_slug": feature_slug,
        "matrix_path": str(matrix_path),
        "agent_count_expected": agent_count_expected,
        "row_count_observed": row_count_observed,
        "findings": findings,
        "verdict": verdict,
        "elapsed_ms": int((time.monotonic() - start) * 1000),
    }
    print(json.dumps(result, indent=2))
    return 1 if has_findings else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 — top-level catch-all per ADR-0035
        err = {
            "sa14_status": "error",
            "feature_slug": "<unknown>",
            "findings": [
                {
                    "rule": RULE_MISSING,
                    "target": "<unknown>",
                    "divergence": f"Unexpected error: {type(exc).__name__}: {exc}",
                    "next_action": "Inspect the traceback on stderr.",
                    "severity": "BLOCKER",
                }
            ],
            "verdict": "FAIL",
        }
        print(json.dumps(err, indent=2), file=sys.stderr)
        sys.exit(2)
