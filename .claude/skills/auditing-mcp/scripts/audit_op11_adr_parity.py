#!/usr/bin/env python3
"""
audit_op11_adr_parity.py — OP-11 .mcp.json ↔ ADR-0041 invocation-form parity rule.

For every server in .mcp.json, verify that a matching row exists in ADR-0041's
per-server invocation-form table (active or deprecated), and that the invocation
form documented in the active row matches the actual .mcp.json entry.

Deprecated-row semantics (rows annotated with [DEPRECATED INVOCATION FORM):
  - A deprecated ADR row for server X counts as "ADR-0041 knows about X" —
    so X in .mcp.json does NOT trigger a missing-in-adr-0041 BLOCKER.
  - A deprecated ADR row for server X does NOT require X to be in .mcp.json —
    so a deprecated-only server with no .mcp.json entry does NOT trigger
    absent-from-mcp-json.
  - Form-parity comparison is SKIPPED for servers whose only ADR row is deprecated
    (the form is known to have changed; the annotation records the historical form
    for audit-trail purposes per ADR-0005 append-only discipline).

Active rows (no [DEPRECATED INVOCATION FORM annotation):
  - Every active row's server MUST be present in .mcp.json (absent-from-mcp-json).
  - Every .mcp.json server that has NO ADR row at all triggers missing-in-adr-0041.
  - Form-parity: the .mcp.json invocation form must match at least one backtick-quoted
    invocation block from the ADR form cell (the ADR may document multiple forms —
    install, MCP-server invocation, smoke-test — and matching ANY one is sufficient).

Canonicalization and matching:
  - Whitespace runs collapsed to single space, leading/trailing stripped.
  - Surrounding double-quotes stripped from each token before comparison.
  - ${VAR} env-var placeholders are opaque tokens (never expanded; NFR-7/NFR-8).
  - HTTP servers match on URL equality.

Exit codes:
  0 — no findings (clean)
  1 — at least one BLOCKER finding
  2 — internal error (cannot parse .mcp.json or ADR-0041)

FR-6 diagnostic (four fields) is emitted to stderr on exit 1.

Usage:
    python3 audit_op11_adr_parity.py [<mcp_json_path>] [<adr_0041_path>]
    python3 audit_op11_adr_parity.py --selftest

Default paths resolve relative to the project root (five directories above this script).
"""
import json
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

_SCRIPT_DIR = Path(__file__).resolve().parent
# Full path: <project_root>/.claude/skills/auditing-mcp/scripts/<file>
# _SCRIPT_DIR is the scripts/ dir; four .parent calls reach the project root:
#   scripts/ → auditing-mcp/ → skills/ → .claude/ → project_root/
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent.parent.parent


def _default_mcp_json() -> Path:
    return _PROJECT_ROOT / ".mcp.json"


def _default_adr_0041() -> Path:
    candidates = sorted(_PROJECT_ROOT.glob("adrs/ADR-0041-*.md"))
    if candidates:
        return candidates[0]
    return _PROJECT_ROOT / "adrs" / "ADR-0041-install-mechanism-hybrid.md"


# ---------------------------------------------------------------------------
# Canonicalization
# ---------------------------------------------------------------------------

_ENV_VAR_RE = re.compile(r'^\$\{[^}]+\}$')
_WHITESPACE_RE = re.compile(r'\s+')


def _strip_outer_quotes(token: str) -> str:
    """Remove surrounding double-quotes from a token if present."""
    if len(token) >= 2 and token.startswith('"') and token.endswith('"'):
        return token[1:-1]
    return token


def _canonicalize(text: str) -> str:
    """Collapse whitespace runs to a single space and strip leading/trailing space."""
    return _WHITESPACE_RE.sub(" ", text).strip()


def _tokens_equal(a: str, b: str) -> bool:
    """True if two canonicalized strings match with opaque ${VAR} token equality.

    Before comparing, surrounding double-quotes are stripped from each token so
    that 'npx -y "gitnexus@${TAG}" mcp' matches 'npx -y gitnexus@${TAG} mcp'.

    Each ${...} placeholder compares equal to any other ${...} placeholder at the
    same position regardless of variable name (audit never reads env values; NFR-7/8).
    """
    a_tokens = [_strip_outer_quotes(t) for t in a.split()]
    b_tokens = [_strip_outer_quotes(t) for t in b.split()]
    if len(a_tokens) != len(b_tokens):
        return False
    for ta, tb in zip(a_tokens, b_tokens):
        if _ENV_VAR_RE.match(ta) and _ENV_VAR_RE.match(tb):
            continue  # both placeholders → opaque match
        if _ENV_VAR_RE.match(ta) or _ENV_VAR_RE.match(tb):
            return False  # one placeholder, one literal → mismatch
        if ta != tb:
            return False
    return True


# ---------------------------------------------------------------------------
# ADR-0041 table parser
# ---------------------------------------------------------------------------

_DEPRECATED_MARKER = "[DEPRECATED INVOCATION FORM"
_TABLE_HEADER_RE = re.compile(r'\|\s*Server\s*\|\s*Mechanism\s*\|\s*Form\s*\|', re.IGNORECASE)
_TABLE_ROW_RE = re.compile(r'^\s*\|(.+)\|(.+)\|(.+)\|\s*$')
_TABLE_SEPARATOR_RE = re.compile(r'^\s*\|[-| ]+\|\s*$')
_BOLD_RE = re.compile(r'\*\*([^*]+)\*\*')


def parse_adr_table(adr_text: str) -> tuple[list[dict], list[dict]]:
    """Parse the per-server invocation table from ADR-0041 text.

    Returns (active_rows, deprecated_rows) where each row is a dict with keys:
      server, mechanism, form (all stripped strings).
    Bold markdown (**text**) is stripped from cell values.
    The header row and separator rows are excluded.
    """
    lines = adr_text.splitlines()
    in_table = False
    active_rows: list[dict] = []
    deprecated_rows: list[dict] = []

    for line in lines:
        if not in_table:
            if _TABLE_HEADER_RE.search(line):
                in_table = True
            continue

        if not line.strip().startswith("|"):
            if line.strip() == "":
                continue
            break

        if _TABLE_SEPARATOR_RE.match(line):
            continue

        m = _TABLE_ROW_RE.match(line)
        if not m:
            continue

        server = _BOLD_RE.sub(r'\1', m.group(1).strip()).strip()
        mechanism = _BOLD_RE.sub(r'\1', m.group(2).strip()).strip()
        form = _BOLD_RE.sub(r'\1', m.group(3).strip()).strip()

        if server.lower() in ("server", "---", ""):
            continue

        row = {"server": server, "mechanism": mechanism, "form": form}
        if _DEPRECATED_MARKER in form:
            deprecated_rows.append(row)
        else:
            active_rows.append(row)

    return active_rows, deprecated_rows


# ---------------------------------------------------------------------------
# .mcp.json → invocation form string
# ---------------------------------------------------------------------------

def mcp_entry_to_form(name: str, entry: dict) -> str | None:
    """Derive a canonical invocation-form string from a .mcp.json entry.

    For command-based entries: '<command> [args...]'.
    For HTTP entries (type: http): the URL.
    Returns None for unrecognised shapes.
    """
    if entry.get("type") == "http":
        url = entry.get("url", "")
        return url if url else None

    command = entry.get("command", "")
    if command:
        args = entry.get("args", []) or []
        parts = [command] + [str(a) for a in args]
        return " ".join(parts)

    return None


# ---------------------------------------------------------------------------
# ADR-0041 row → candidate form strings for matching
# ---------------------------------------------------------------------------

def adr_row_candidate_forms(row: dict) -> list[str]:
    """Return all candidate invocation forms from an active ADR row.

    For HTTP rows: returns the URL.
    For command rows: returns every backtick-quoted block that looks like a CLI
    invocation (starts with an alphanumeric/path character). If no backtick block is
    found, falls back to the bare form text stripped of annotation markers.

    Returning multiple candidates lets the audit match against the MCP-server-
    invocation block even when the ADR form cell also documents install and smoke-
    test commands.
    """
    form = row["form"]
    mechanism = row["mechanism"]

    # HTTP servers — extract URL
    if "no install (remote HTTP)" in mechanism or "http" in mechanism.lower():
        url_m = re.search(r'https?://\S+', form)
        if url_m:
            url = re.sub(r'[`|>\]\).,]+$', '', url_m.group(0))
            return [url]
        return [form]

    # Command-based — collect all backtick blocks that look like CLI invocations
    candidates = []
    for block in re.findall(r'`([^`]+)`', form):
        block = block.strip()
        if block and re.match(r'^[a-zA-Z0-9._/-]', block):
            candidates.append(block)

    if candidates:
        return candidates

    # No backtick blocks — strip annotation markers and use bare form text
    bare = re.sub(r'\[.*', '', form).strip()
    return [bare] if bare else [form]


def _server_name_matches_command(server_name: str, mcp_form: str) -> bool:
    """True if the .mcp.json invocation is just the binary named after the server, with no args.

    Handles the 'binary on PATH' pattern: a server named 'foo-bar' installed as a
    binary 'foo-bar' invoked with no args. The ADR may document the install mechanism
    rather than the runtime invocation for such servers; this fallback accepts the
    no-args binary invocation as inherently correct.

    Extra args disqualify the fallback — if args are present, the caller must match
    an explicit ADR form.
    """
    tokens = mcp_form.split() if mcp_form else []
    if len(tokens) != 1:
        return False
    return _norm(tokens[0]) == _norm(server_name)


# ---------------------------------------------------------------------------
# Server-name normalisation
# ---------------------------------------------------------------------------

def _norm(name: str) -> str:
    """Case-insensitive, punctuation-stripped name for lookup."""
    return re.sub(r'[^a-z0-9-]', '', name.lower())


# ---------------------------------------------------------------------------
# Core audit
# ---------------------------------------------------------------------------

def run_audit(mcp_json_path: Path, adr_path: Path) -> tuple[int, list[dict]]:
    """Run the OP-11 parity check. Returns (exit_code, findings)."""

    try:
        mcp_cfg = json.loads(mcp_json_path.read_text())
    except (OSError, json.JSONDecodeError) as e:
        _emit_error(f"cannot load .mcp.json: {e}")
        return 2, []

    try:
        adr_text = adr_path.read_text()
    except OSError as e:
        _emit_error(f"cannot read ADR-0041: {e}")
        return 2, []

    active_rows, deprecated_rows = parse_adr_table(adr_text)
    if not active_rows and not deprecated_rows:
        _emit_error(f"no rows found in ADR-0041 table at {adr_path}")
        return 2, []

    mcp_servers: dict[str, dict] = mcp_cfg.get("mcpServers", {})

    # Build normalised-name lookup maps
    mcp_by_norm = {_norm(n): (n, e) for n, e in mcp_servers.items()}
    active_by_norm = {_norm(r["server"]): r for r in active_rows}
    deprecated_by_norm = {_norm(r["server"]): r for r in deprecated_rows}
    all_known_norms = set(active_by_norm) | set(deprecated_by_norm)

    findings: list[dict] = []

    # Check 1: every .mcp.json server must have at least one ADR row (active or deprecated)
    for norm, (orig_name, _entry) in mcp_by_norm.items():
        if norm not in all_known_norms:
            findings.append({
                "rule": "OP-11",
                "severity": "BLOCKER",
                "server": orig_name,
                "field": "missing-in-adr-0041",
                "message": (
                    f"Server '{orig_name}' is in .mcp.json but has no row (active or "
                    f"deprecated) in ADR-0041's per-server invocation table."
                ),
                "remediation": (
                    f"Add a row for '{orig_name}' to the per-server table in ADR-0041."
                ),
            })

    # Check 2: every active ADR row must have a .mcp.json entry
    # Deprecated rows are exempt — a deprecated row does NOT require .mcp.json presence.
    for norm, row in active_by_norm.items():
        if norm not in mcp_by_norm:
            findings.append({
                "rule": "OP-11",
                "severity": "BLOCKER",
                "server": row["server"],
                "field": "absent-from-mcp-json",
                "message": (
                    f"ADR-0041 has an active (non-deprecated) row for '{row['server']}' "
                    f"but this server is not present in .mcp.json."
                ),
                "remediation": (
                    f"Add '{row['server']}' to .mcp.json, or annotate its ADR-0041 row "
                    f"with [DEPRECATED INVOCATION FORM if the server has been removed."
                ),
            })

    # Check 3: form-parity for servers present in both .mcp.json and an active ADR row.
    # Servers whose only ADR row is deprecated have no active form to compare — skip.
    for norm in set(mcp_by_norm) & set(active_by_norm):
        orig_name, entry = mcp_by_norm[norm]
        row = active_by_norm[norm]

        mcp_form = mcp_entry_to_form(orig_name, entry)
        if mcp_form is None:
            findings.append({
                "rule": "OP-11",
                "severity": "BLOCKER",
                "server": orig_name,
                "field": "invocation-form-mismatch",
                "message": (
                    f"Cannot derive invocation form for '{orig_name}' from .mcp.json "
                    f"(entry has neither 'command' nor 'type: http')."
                ),
                "remediation": (
                    "Ensure the .mcp.json entry has either a 'command' field or 'type: http'."
                ),
            })
            continue

        mcp_canon = _canonicalize(mcp_form)
        candidates = adr_row_candidate_forms(row)

        # Primary: token-equal match against any ADR candidate form.
        # Fallback: binary-on-PATH pattern — server invoked by its own name with no
        # extra args (ADR documents the install mechanism, not the runtime invocation).
        matched = (
            any(_tokens_equal(mcp_canon, _canonicalize(c)) for c in candidates)
            or _server_name_matches_command(orig_name, mcp_form)
        )
        if not matched:
            adr_candidates_display = [_canonicalize(c) for c in candidates]
            findings.append({
                "rule": "OP-11",
                "severity": "BLOCKER",
                "server": orig_name,
                "field": "invocation-form-mismatch",
                "message": (
                    f"Invocation form mismatch for '{orig_name}'. "
                    f".mcp.json: '{mcp_canon}'. "
                    f"ADR-0041 candidates: {adr_candidates_display}."
                ),
                "remediation": (
                    f"Align the .mcp.json entry for '{orig_name}' with a form documented "
                    f"in ADR-0041, or amend ADR-0041 to reflect the current form."
                ),
            })

    return (1 if findings else 0), findings


# ---------------------------------------------------------------------------
# FR-6 diagnostic output
# ---------------------------------------------------------------------------

def _fr6_diagnostic(findings: list[dict], mcp_path: Path, adr_path: Path) -> str:
    lines = ["OP-11 .mcp.json ↔ ADR-0041 parity — BLOCKER findings:\n"]
    for f in findings:
        lines.append(f"  Mechanism : OP-11 .mcp.json ↔ ADR-0041 parity")
        lines.append(f"  Artifact  : server '{f['server']}' — {f['field']}")
        lines.append(f"  Violated  : {f['message']}")
        lines.append(f"  Remediate : {f['remediation']}")
        lines.append("")
    lines.append(f"  Inputs checked:")
    lines.append(f"    .mcp.json : {mcp_path}")
    lines.append(f"    ADR-0041  : {adr_path}")
    return "\n".join(lines)


def _emit_error(msg: str) -> None:
    print(json.dumps({"error": msg}), file=sys.stderr)


# ---------------------------------------------------------------------------
# Self-test harness
# ---------------------------------------------------------------------------

def run_selftest() -> int:
    """Run all fixtures from working/feature/.../fixtures/fr3/ and report results."""
    fixture_dir = (
        _PROJECT_ROOT
        / "working"
        / "feature"
        / "pipeline-quickwins-hardening-r1"
        / "fixtures"
        / "fr3"
    )

    if not fixture_dir.exists():
        print(f"[selftest] fixture directory not found: {fixture_dir}", file=sys.stderr)
        return 2

    test_cases = [
        # (label, mcp_file, adr_file, expected_exit_code)
        ("clean pair (exit 0)", "clean_mcp_json.json", "clean_adr_table.md", 0),
        ("missing in ADR (exit 1)", "missing_in_adr.json", "missing_in_adr_table.md", 1),
        ("absent from mcp (exit 1)", "absent_from_mcp.json", "absent_from_mcp_table.md", 1),
        ("form mismatch (exit 1)", "form_mismatch.json", "form_mismatch_table.md", 1),
        ("deprecated row skip (exit 0)", "deprecated_row_skip.json", "deprecated_row_skip_table.md", 0),
        ("live repo state (exit 0)", "live_mcp.json", "live_adr_table.md", 0),
    ]

    passed = 0
    failed = 0

    for label, mcp_file, adr_file, expected in test_cases:
        mcp_path = fixture_dir / mcp_file
        adr_path = fixture_dir / adr_file

        if not mcp_path.exists():
            print(f"[selftest] SKIP  {label}: fixture missing {mcp_path.name}")
            continue
        if not adr_path.exists():
            print(f"[selftest] SKIP  {label}: fixture missing {adr_path.name}")
            continue

        code, _ = run_audit(mcp_path, adr_path)
        status = "PASS" if code == expected else "FAIL"
        suffix = "" if code == expected else f": expected exit {expected}, got {code}"
        print(f"[selftest] {status}  {label}{suffix}")
        if code == expected:
            passed += 1
        else:
            failed += 1

    total = passed + failed
    print(f"\n[selftest] {passed}/{total} passed")
    return 0 if failed == 0 else 1


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    args = sys.argv[1:]

    if "--selftest" in args:
        return run_selftest()

    mcp_path = Path(args[0]).resolve() if len(args) >= 1 else _default_mcp_json()
    adr_path = Path(args[1]).resolve() if len(args) >= 2 else _default_adr_0041()

    if not mcp_path.exists():
        _emit_error(f".mcp.json not found: {mcp_path}")
        return 2

    if not adr_path.exists():
        _emit_error(f"ADR-0041 not found: {adr_path}")
        return 2

    exit_code, findings = run_audit(mcp_path, adr_path)

    result = {
        "rule": "OP-11",
        "name": ".mcp.json ↔ ADR-0041 invocation-form parity",
        "mcp_json": str(mcp_path),
        "adr_0041": str(adr_path),
        "findings": findings,
    }
    print(json.dumps(result, indent=2))

    if exit_code == 1:
        print(_fr6_diagnostic(findings, mcp_path, adr_path), file=sys.stderr)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
