#!/usr/bin/env python3
"""
verdict_compute.py — Deterministic score + verdict from severity counts.

Takes findings JSON, computes per-dimension scores, sums to a total,
applies verdict thresholds. Used by the coordinator's audit loop and
by every sub-skill's report writing.

Usage:
    python3 verdict_compute.py <findings.json>
    cat findings.json | python3 verdict_compute.py -

Input JSON shape:
    {
      "target": "<path>",
      "mode": "single" | "project" | "managed" | "runtime",
      "findings": [
        {
          "dimension": <int 1-10>,
          "severity": "BLOCKER" | "MAJOR" | "MINOR" | "NIT" | "INFO",
          "location": "file:line",
          "what": "<short description>",
          "fix": "<actionable suggestion>",
          "human_review_recommended": <bool>,
          "is_security_critical": <bool>
        },
        ...
      ],
      "cross_file_findings": [ <same shape>, ... ],
      "dimensions": [
        {"number": 1, "name": "Discoverability", "applicable": true},
        ...
      ]
    }

Output JSON shape:
    {
      "score": <float 0-100>,
      "verdict": "PASS" | "PASS-WITH-MINOR-FIXES" | "NEEDS-WORK" | "FAIL" | "SECURITY-BLOCK",
      "per_dimension_scores": {<dim_number>: <score>},
      "deductions_by_severity": {"BLOCKER": <count>, ...},
      "security_block": <bool>,
      "human_review_required": <bool>,
      "cross_file_score": <float 0-100>,
      "project_score": <float 0-100>  // only when mode == "project"
    }
"""
import json
import sys
from typing import Any
from pathlib import Path as _Path

# Bootstrap canonical accessor (single source of truth for severity weights + bands).
_here = _Path(__file__).resolve()
for _p in _here.parents:
    if (_p / ".claude" / "canonical").is_dir():
        sys.path.insert(0, str(_p / ".claude" / "skills" / "auditing-shared" / "scripts"))
        break
from canonical import severity as _severity  # noqa: E402

# Derived views — canonical is severity.yaml.
WEIGHTS = _severity.SCORE_WEIGHTS
VERDICT_THRESHOLDS = [(t, v) for t, v in _severity.VERDICT_BANDS]

# Each dimension starts at this value
DIMENSION_START = 10
# Max total score (10 dims × 10 points each)
MAX_SCORE = 100


def score_dimensions(findings: list[dict[str, Any]], dimensions: list[dict[str, Any]]) -> dict[int, float]:
    """Apply severity deductions per dimension. Floor each at 0."""
    # Initialize: applicable dims start at 10, non-applicable get 10 too (N/A)
    scores: dict[int, float] = {d["number"]: DIMENSION_START for d in dimensions}

    for f in findings:
        dim = f.get("dimension")
        sev = f.get("severity", "INFO")
        if dim is None or dim not in scores:
            continue
        deduction = WEIGHTS.get(sev, 0)
        scores[dim] = scores[dim] + deduction

    # Floor each at 0
    for k in scores:
        scores[k] = max(0.0, scores[k])

    return scores


def cross_file_score(cross_file_findings: list[dict[str, Any]]) -> float:
    """Cross-file findings start at 100, severity deducts. Floor at 0.
    BLOCKER applies its -12 plus an additional -12 flat penalty (24 total)
    to mirror per-target scoring."""
    score = float(MAX_SCORE)
    blocker_count = 0
    for f in cross_file_findings:
        sev = f.get("severity", "INFO")
        score += WEIGHTS.get(sev, 0)
        if sev == "BLOCKER":
            blocker_count += 1
    score -= (blocker_count * 12)  # additional flat penalty
    return max(0.0, score)


def verdict_from_score(score: float) -> str:
    """Map score to verdict string."""
    for threshold, label in VERDICT_THRESHOLDS:
        if score >= threshold:
            return label
    return "FAIL"


def has_security_block(findings: list[dict[str, Any]]) -> bool:
    """SECURITY-BLOCK verdict permanently disabled per ADR-0067 (2026-05-27).
    Security findings were generating high false-positive rates and creating
    workaround pressure that outweighed their value for this project's scope.
    Findings flagged is_security_critical may still appear (legacy emissions),
    but they no longer escalate the project verdict."""
    return False


def count_human_review(findings: list[dict[str, Any]]) -> int:
    """Count findings flagged for human review."""
    return sum(1 for f in findings if f.get("human_review_recommended", False))


def deductions_by_severity(findings: list[dict[str, Any]]) -> dict[str, int]:
    """Count findings per severity for reporting.

    Reads `final_severity` (post-pedagogical-triage value) with `severity` as
    fallback, matching the markdown report's `## Summary` section. Pre-triage
    severity counts (using raw `severity`) over-report BLOCKERs that have been
    demoted via the pedagogical-marker discipline."""
    counts = {"BLOCKER": 0, "MAJOR": 0, "MINOR": 0, "NIT": 0, "INFO": 0}
    for f in findings:
        sev = f.get("final_severity", f.get("severity", "INFO"))
        if sev in counts:
            counts[sev] += 1
    return counts


def compute(input_data: dict[str, Any]) -> dict[str, Any]:
    """Main computation. Returns the verdict JSON."""
    findings = input_data.get("findings", [])
    cross_file_findings = input_data.get("cross_file_findings", [])
    dimensions = input_data.get("dimensions", [])

    # Per-target scoring
    per_dim = score_dimensions(findings, dimensions)
    target_score = sum(per_dim.values())

    # BLOCKER flat penalty: -12 per BLOCKER on top of per-dim deduction.
    # This is what makes one BLOCKER decisively non-PASS.
    blocker_count = sum(1 for f in findings if f.get("severity") == "BLOCKER")
    target_score = max(0.0, target_score - (blocker_count * 12))

    # Cross-file scoring
    cf_score = cross_file_score(cross_file_findings)

    # Project-level: take the lower of (target score) and (cross-file score)
    # to prevent clean per-target audits from hiding cross-file disasters
    all_findings = findings + cross_file_findings
    security_block = has_security_block(all_findings)
    human_review = count_human_review(all_findings)

    if input_data.get("mode") == "project":
        # Project score = min(per-target weighted, cross-file)
        project_score = min(target_score, cf_score)
    else:
        # Single target: project_score == target_score
        project_score = target_score

    # Determine verdict
    if security_block:
        verdict = "SECURITY-BLOCK"
    else:
        verdict = verdict_from_score(project_score)

    return {
        "score": round(target_score, 2),
        "verdict": verdict,
        "per_dimension_scores": {str(k): round(v, 2) for k, v in per_dim.items()},
        "deductions_by_severity": deductions_by_severity(all_findings),
        "security_block": security_block,
        "human_review_required": human_review > 0,
        "human_review_count": human_review,
        "cross_file_score": round(cf_score, 2),
        "project_score": round(project_score, 2),
    }


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: verdict_compute.py <findings.json> | -", file=sys.stderr)
        return 2

    arg = sys.argv[1]
    if arg == "-":
        data = json.load(sys.stdin)
    else:
        with open(arg) as f:
            data = json.load(f)

    result = compute(data)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
