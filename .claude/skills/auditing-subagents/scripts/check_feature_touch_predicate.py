#!/usr/bin/env python3
"""check_feature_touch_predicate.py — Advisory predicate for FR-6 agent-surface touch detection.

Evaluates whether the current feature run has touched the agent surface across
four trigger conditions defined in ADR-0064 Clause 1 and FR-6 of
pipeline-design-time-discipline-r1.  When one or more conditions fire, the
predicate advises the human author (design-cc) to produce the
agent-roster-impact-matrix.md artifact.

This predicate is ADVISORY — exit code 1 means "matrix authoring recommended",
NOT a hard failure.  The hard gate is FR-10's SA-14 audit rule which runs at
deliverable packaging time.

Trigger conditions (ADR-0064 Clause 1):
  1. git diff modifies/creates/removes any .claude/agents/*.md file
  2. git diff modifies .mcp.json adding/removing/changing MCP server tool surface
  3. This feature run creates a new skill (new .claude/skills/*/SKILL.md)
     that the design indicates an existing agent will load — MECHANICAL ONLY,
     mechanical_only: true; design-cc ratifies
  4. This feature's design or PRD declares a new domain concept whose
     skill-coverage decision names an existing agent — MECHANICAL ONLY via
     grep heuristics; design-cc ratifies

References:
  ADR-0064 — Agent-Roster Impact Matrix Contract (Clause 1, Clause 3)
  FR-6 — pipeline-design-time-discipline-r1 PRD

Exit codes:
  0 = predicate did not fire (no agent-surface touches detected)
  1 = predicate fired (matrix authoring is recommended) — advisory, NOT failure
  2 = invocation error (missing args, can't find feature-slug, git unavailable)

Output: JSON to stdout, log messages to stderr.
Python 3.8+ stdlib only.
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

_AGENTS_GLOB = ".claude/agents/*.md"
_MCP_JSON_PATH = ".mcp.json"
_SKILL_PATTERN = re.compile(r"^\.claude/skills/([^/]+)/SKILL\.md$")

# Heuristics for condition 4 — grep for tokens that suggest skill-coverage
# decisions naming an existing agent as downstream consumer.
_SKILL_COVERAGE_PATTERNS = [
    re.compile(r"skill-coverage decision", re.IGNORECASE),
    re.compile(r"Skill-Coverage Decisions", re.IGNORECASE),
    re.compile(r"new domain concept", re.IGNORECASE),
    re.compile(r"existing agent", re.IGNORECASE),
]

# Tokens in .mcp.json diff that suggest tool-surface changes on allowlisted servers.
_MCP_TOOL_SURFACE_PATTERNS = [
    re.compile(r'"tools"\s*:'),
    re.compile(r'"allowed_tools"\s*:'),
    re.compile(r'"allowedTools"\s*:'),
    re.compile(r'"allowlist"\s*:'),
    re.compile(r'^\+.*"name"\s*:', re.MULTILINE),
    re.compile(r'^-.*"name"\s*:', re.MULTILINE),
]


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def _run_git(args: List[str], cwd: str) -> Tuple[int, str, str]:
    """Run a git command; return (returncode, stdout, stderr)."""
    try:
        r = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=cwd,
        )
        return r.returncode, r.stdout, r.stderr
    except FileNotFoundError:
        return 2, "", "git not found in PATH"
    except subprocess.TimeoutExpired:
        return 2, "", "git command timed out"


def _git_diff_names(ref_baseline: str, cwd: str) -> Tuple[Optional[List[str]], Optional[str]]:
    """Return list of files changed vs *ref_baseline*, or (None, error_msg).

    Combines three sources:
      1. git diff --name-only <ref_baseline> — tracked files changed since baseline
      2. git diff --name-only --cached         — staged (index) changes
      3. git ls-files --others --exclude-standard — untracked new files
    """
    names: set = set()

    # Source 1: tracked changes vs baseline
    code, out, _ = _run_git(
        ["diff", "--name-only", ref_baseline, "--", "."],
        cwd=cwd,
    )
    if out.strip():
        names.update(out.splitlines())

    # Source 2: staged (index) changes vs baseline (catches `git add`-ed new files)
    code2, out2, _ = _run_git(
        ["diff", "--name-only", "--cached", ref_baseline, "--", "."],
        cwd=cwd,
    )
    if out2.strip():
        names.update(out2.splitlines())

    # Source 3: untracked files not yet staged (new files created in working tree)
    # Use --exclude-standard to respect .gitignore.
    # This lists individual file paths, not directory summaries.
    code3, out3, _ = _run_git(
        ["ls-files", "--others", "--exclude-standard"],
        cwd=cwd,
    )
    if out3.strip():
        names.update(f.strip() for f in out3.splitlines() if f.strip())

    # Also include modified-but-unstaged files from porcelain status
    code4, out4, _ = _run_git(
        ["status", "--short", "--porcelain"],
        cwd=cwd,
    )
    for line in out4.splitlines():
        if len(line) >= 3:
            xy = line[:2]
            fname = line[3:].strip()
            # Include modified (M), added (A), deleted (D); skip untracked (??)
            # already covered by ls-files above, and directory summaries (end /)
            if not fname.endswith("/") and xy.strip() in ("M", "A", "D", "AM", "AD", "MM", "R"):
                names.add(fname)

    return list(names), None


def _git_diff_content(ref_baseline: str, path: str, cwd: str) -> Optional[str]:
    """Return unified diff content for a specific path vs *ref_baseline*."""
    code, out, _ = _run_git(
        ["diff", ref_baseline, "--", path],
        cwd=cwd,
    )
    return out if out else None


def _git_is_available(cwd: str) -> Tuple[bool, str]:
    """Check if git is available and cwd is inside a repo."""
    code, out, err = _run_git(["rev-parse", "--git-dir"], cwd=cwd)
    if code != 0:
        return False, f"git rev-parse failed: {err.strip()}"
    return True, ""


# ---------------------------------------------------------------------------
# Feature-slug resolution
# ---------------------------------------------------------------------------

def _resolve_feature_slug(slug: Optional[str], repo_root: str) -> Tuple[Optional[str], Optional[str]]:
    """Return (resolved_slug, error_msg).

    If *slug* is given, verify working/feature/<slug>/ exists.
    Otherwise find the most recently modified working/feature/<slug>/ directory.
    """
    working_features = Path(repo_root) / "working" / "feature"
    if slug:
        candidate = working_features / slug
        if not candidate.is_dir():
            return None, f"feature directory not found: {candidate}"
        return slug, None

    # Auto-discover: find the most recently modified feature dir
    if not working_features.is_dir():
        return None, f"working/feature/ directory not found at {working_features}"

    candidates = [d for d in working_features.iterdir() if d.is_dir()]
    if not candidates:
        return None, "no feature directories found under working/feature/"

    # Sort by mtime descending
    candidates.sort(key=lambda d: d.stat().st_mtime, reverse=True)
    return candidates[0].name, None


def _get_repo_root(cwd: str) -> Tuple[Optional[str], Optional[str]]:
    """Return (repo_root_path, error_msg)."""
    code, out, err = _run_git(["rev-parse", "--show-toplevel"], cwd=cwd)
    if code != 0:
        return None, f"could not determine repo root: {err.strip()}"
    return out.strip(), None


# ---------------------------------------------------------------------------
# Condition evaluators
# ---------------------------------------------------------------------------

def _condition_1(changed_files: List[str]) -> Optional[Dict]:
    """Condition 1: any .claude/agents/*.md file modified/created/removed."""
    agent_files = [
        f for f in changed_files
        if re.match(r"^\.claude/agents/[^/]+\.md$", f)
    ]
    if not agent_files:
        return None
    return {
        "condition": "1",
        "description": "git diff modifies/creates/removes .claude/agents/*.md",
        "evidence": f"{len(agent_files)} agent file(s) touched",
        "files": sorted(agent_files),
        "mechanical_only": False,
    }


def _condition_2(changed_files: List[str], ref_baseline: str, cwd: str) -> Optional[Dict]:
    """Condition 2: .mcp.json modified in a way affecting tool surface."""
    if _MCP_JSON_PATH not in changed_files:
        return None

    diff_content = _git_diff_content(ref_baseline, _MCP_JSON_PATH, cwd) or ""
    if not diff_content:
        # File changed but no diff content available — conservative: fire advisory
        return {
            "condition": "2",
            "description": ".mcp.json modified (diff unavailable; conservative fire)",
            "evidence": ".mcp.json appears in changed files list; diff not retrievable",
            "files": [_MCP_JSON_PATH],
            "mechanical_only": False,
        }

    matched_patterns = []
    for pat in _MCP_TOOL_SURFACE_PATTERNS:
        if pat.search(diff_content):
            matched_patterns.append(pat.pattern)

    if not matched_patterns:
        # .mcp.json changed but no tool-surface tokens detected — do not fire
        return None

    return {
        "condition": "2",
        "description": ".mcp.json modified with tool-surface changes to allowlisted MCP servers",
        "evidence": f"diff contains tool-surface tokens: {matched_patterns[:3]}",
        "files": [_MCP_JSON_PATH],
        "mechanical_only": False,
    }


def _condition_3(changed_files: List[str]) -> Optional[Dict]:
    """Condition 3: new SKILL.md files created — mechanical detection only.

    Cannot determine mechanically whether an existing agent 'will load' the
    skill; design-cc ratifies (mechanical_only: true per ADR-0064 Clause 3).
    """
    new_skills = []
    for f in changed_files:
        m = _SKILL_PATTERN.match(f)
        if m:
            new_skills.append((f, m.group(1)))

    if not new_skills:
        return None

    return {
        "condition": "3",
        "description": "new SKILL.md file(s) created — design-cc must ratify agent-load relationship",
        "evidence": (
            f"{len(new_skills)} new SKILL.md file(s) detected: "
            + ", ".join(name for _, name in new_skills[:5])
            + (" ..." if len(new_skills) > 5 else "")
        ),
        "files": sorted(f for f, _ in new_skills),
        "mechanical_only": True,
    }


def _condition_4(feature_slug: str, repo_root: str) -> Optional[Dict]:
    """Condition 4: design.md / PRD.md references skill-coverage decision naming an existing agent.

    Mechanical detection via grep heuristics on the feature's design and PRD
    artifacts.  Cannot determine authoritative truth; design-cc ratifies
    (mechanical_only: true per ADR-0064 Clause 3).
    """
    feature_dir = Path(repo_root) / "working" / "feature" / feature_slug
    if not feature_dir.is_dir():
        return None

    # Candidate files: any .md file in the feature directory (top-level)
    candidate_files = list(feature_dir.glob("*.md"))
    if not candidate_files:
        return None

    triggered_files = []
    for md_file in candidate_files:
        try:
            text = md_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for pat in _SKILL_COVERAGE_PATTERNS:
            if pat.search(text):
                triggered_files.append(str(md_file.relative_to(repo_root)))
                break  # one pattern match per file is enough

    if not triggered_files:
        return None

    return {
        "condition": "4",
        "description": (
            "feature design/PRD declares new domain concept with skill-coverage "
            "decision — design-cc must confirm agent naming relationship"
        ),
        "evidence": (
            f"heuristic tokens matched in {len(triggered_files)} file(s): "
            + ", ".join(triggered_files[:3])
            + (" ..." if len(triggered_files) > 3 else "")
        ),
        "files": sorted(triggered_files),
        "mechanical_only": True,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    start = time.monotonic()

    parser = argparse.ArgumentParser(
        description=(
            "Advisory predicate: detect whether this feature run touches the agent "
            "surface and advise design-cc to produce agent-roster-impact-matrix.md. "
            "Exit 0 = predicate silent; exit 1 = predicate fires (advisory); "
            "exit 2 = invocation error."
        ),
        epilog=(
            "Per ADR-0064 Clause 3: exit code 1 is ADVISORY (matrix recommended), "
            "NOT a hard failure.  The human designer ratifies."
        ),
    )
    parser.add_argument(
        "--feature-slug",
        default=None,
        help=(
            "Feature slug to evaluate (e.g. 'pipeline-design-time-discipline-r1'). "
            "Defaults to auto-discovering the most recently modified "
            "working/feature/<slug>/ directory."
        ),
    )
    parser.add_argument(
        "--ref-baseline",
        default="HEAD",
        help="git ref to diff against (default: HEAD).",
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help=(
            "Explicit repo root path. Defaults to git rev-parse --show-toplevel "
            "from the current working directory."
        ),
    )
    args = parser.parse_args()

    cwd = os.getcwd()

    # Step 1: verify git availability
    git_ok, git_err = _git_is_available(cwd)
    if not git_ok:
        result = {
            "feature_slug": args.feature_slug or "<unknown>",
            "predicate_fired": False,
            "triggers": [],
            "advisory_message": "Invocation error — git not available",
            "error": git_err,
            "elapsed_ms": int((time.monotonic() - start) * 1000),
        }
        print(json.dumps(result, indent=2))
        return 2

    # Step 2: resolve repo root
    if args.repo_root:
        repo_root = str(Path(args.repo_root).resolve())
    else:
        repo_root, repo_err = _get_repo_root(cwd)
        if repo_root is None:
            result = {
                "feature_slug": args.feature_slug or "<unknown>",
                "predicate_fired": False,
                "triggers": [],
                "advisory_message": "Invocation error — cannot determine repo root",
                "error": repo_err,
                "elapsed_ms": int((time.monotonic() - start) * 1000),
            }
            print(json.dumps(result, indent=2))
            return 2

    # Step 3: resolve feature slug
    feature_slug, slug_err = _resolve_feature_slug(args.feature_slug, repo_root)
    if feature_slug is None:
        result = {
            "feature_slug": args.feature_slug or "<unknown>",
            "predicate_fired": False,
            "triggers": [],
            "advisory_message": "Invocation error — cannot resolve feature slug",
            "error": slug_err,
            "elapsed_ms": int((time.monotonic() - start) * 1000),
        }
        print(json.dumps(result, indent=2))
        return 2

    ref_baseline = args.ref_baseline

    # Step 4: collect changed files
    changed_files, diff_err = _git_diff_names(ref_baseline, repo_root)
    if changed_files is None:
        changed_files = []
        print(
            f"WARNING: could not enumerate changed files: {diff_err}",
            file=sys.stderr,
        )

    # Step 5: evaluate the four conditions
    triggers = []

    c1 = _condition_1(changed_files)
    if c1:
        triggers.append(c1)

    c2 = _condition_2(changed_files, ref_baseline, repo_root)
    if c2:
        triggers.append(c2)

    c3 = _condition_3(changed_files)
    if c3:
        triggers.append(c3)

    c4 = _condition_4(feature_slug, repo_root)
    if c4:
        triggers.append(c4)

    predicate_fired = bool(triggers)

    if predicate_fired:
        advisory_message = (
            "Matrix authoring recommended — feature touches agent surface "
            "(per ADR-0064 Clause 1; design-cc must ratify and produce "
            "working/feature/<slug>/agent-roster-impact-matrix.md)"
        )
    else:
        advisory_message = (
            "No matrix required — clean run "
            "(no agent-surface touches detected across all four trigger conditions)"
        )

    result = {
        "feature_slug": feature_slug,
        "predicate_fired": predicate_fired,
        "triggers": triggers,
        "advisory_message": advisory_message,
        "ref_baseline": ref_baseline,
        "changed_files_scanned": len(changed_files),
        "elapsed_ms": int((time.monotonic() - start) * 1000),
    }
    print(json.dumps(result, indent=2))
    return 1 if predicate_fired else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 — top-level catch-all
        err = {
            "feature_slug": "<unknown>",
            "predicate_fired": False,
            "triggers": [],
            "advisory_message": "Invocation error — unexpected exception",
            "error": f"unexpected error: {type(exc).__name__}: {exc}",
        }
        print(json.dumps(err, indent=2), file=sys.stderr)
        sys.exit(2)
