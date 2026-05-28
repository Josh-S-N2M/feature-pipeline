#!/usr/bin/env python3
"""
pedagogical_marker_check.py — Apply the pedagogical-marker triage matrix
and anti-laundering checks to a set of raw findings.

Canonical implementation per ADR-0031 (auditing-shared). Implements mechanism α
per ADR-0030 + spec at:
    KB-documentation-criteria/references/pedagogical-marker-justification-spec.md

Replaces 3 prior copies in auditing-cc-configs, auditing-skills, auditing-subagents
(v4.4.x state) — those copies become subprocess-dispatch shims OR are deleted +
their callers redirected to invoke this canonical script directly.

Mechanism α (in summary): a pedagogical marker (frontmatter `pedagogical_sections:`
entry or block-level ```audit-example``` fence) MUST carry inline justification.
Markers without valid justification are REJECTED — treated as if absent — so the
underlying finding surfaces at original severity. The check also emits a MAJOR
finding of its own per rejected marker.

Backward-compatibility: this canonical script honors BOTH `location` and `where`
finding-keys (defensive get-or-fallback) per AC-FR-12-d. The 3 prior copies used
different keys (skills used `where`; cc-configs + subagents used `location`).

Usage:
    python3 pedagogical_marker_check.py <skill-path> <findings.json>
"""

import json
import re
import sys
from pathlib import Path
from typing import Any
import sys as _sys

# Canonical severity vocabulary (single source of truth).
_here = Path(__file__).resolve()
for _p in _here.parents:
    if (_p / ".claude" / "canonical").is_dir():
        _sys.path.insert(0, str(_p / ".claude" / "skills" / "auditing-shared" / "scripts"))
        break
from canonical import severity as _severity  # noqa: E402

SEVERITY_ORDER = _severity.ORDER

# Fence language that marks block-level pedagogical content
PEDAGOGICAL_FENCE_LANG = "audit-example"

# Patterns that indicate operationally dangerous content regardless of marker
# These trigger the anti-laundering override
DANGEROUS_PATTERNS_LIVE = [
    # High-entropy strings that look like real credentials (not env-var refs)
    # AKIA + 16 alphanumeric (AWS access key ID format)
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    # GitHub fine-grained PAT format
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{82}\b"),
    # GitHub classic PAT
    re.compile(r"\bghp_[A-Za-z0-9]{36}\b"),
    # Anthropic API key
    re.compile(r"\bsk-ant-api03-[A-Za-z0-9_\-]{80,}\b"),
    # OpenAI API key
    re.compile(r"\bsk-proj-[A-Za-z0-9_\-]{40,}\b"),
    # SSH RSA private key markers
    re.compile(r"-----BEGIN (RSA|OPENSSH|EC|DSA) PRIVATE KEY-----"),
]

# Well-known fake/example credential indicators — strings containing these
# substrings (case-insensitive) are treated as documented examples and
# NOT flagged by anti-laundering. Real attackers don't put EXAMPLE in their
# keys.
FAKE_CREDENTIAL_INDICATORS = [
    "EXAMPLE",
    "FAKE",
    "PLACEHOLDER",
    "XXXXXX",
    "YOUR_",
    "REPLACE_ME",
    "1234567890",
    "ABCDEFGH",
]

# Live attacker URLs (anything not in the allowed-example list)
ALLOWED_EXAMPLE_HOSTS = {
    "example.com", "example.org", "example.net",
    "localhost", "127.0.0.1",
    "host.docker.internal",
    "attacker.com",  # commonly used as a known-fake example
    "attacker.example",  # RFC 6761 .example reserved TLD
    "evil.com",       # ditto
    "evil.example",
    "malicious.example",
    "phishing.example",
}

# Match http(s) URLs and SSE/HTTP MCP URLs
URL_PATTERN = re.compile(
    r"https?://([a-zA-Z0-9.\-]+)"  # capture host
)


def finding_location(finding: dict[str, Any]) -> str | None:
    """Backward-compat helper per AC-FR-12-d.

    Prior copies of this script lived at:
      - auditing-cc-configs/scripts/  (used key `location`)
      - auditing-subagents/scripts/    (used key `location`)
      - auditing-skills/scripts/       (used key `where`)

    The canonical script accepts either; consumers passing findings from any
    auditing-* module receive identical behavior. Returns None if neither key
    is present (caller decides what to do).
    """
    return finding.get("location") or finding.get("where")


# --- Mechanism α: justification validity ---
# Per KB-documentation-criteria/references/pedagogical-marker-justification-spec.md
# §4 — three independent rules; all must hold.

_BANNED_BARE_WORDS = frozenset({
    "pedagogical", "example", "examples", "illustrative", "illustration",
    "illustrations", "documentation", "not", "real", "fake", "test",
    "placeholder", "demo", "sample", "showing", "show", "demonstrate",
    "demonstrates", "demonstration",
})
_ARTICLES = frozenset({"a", "an", "the", "is", "are", "this", "that", "these", "those"})

_SUBSTANCE_KEYWORDS_FILE = (
    Path(__file__).resolve().parent.parent.parent
    / "KB-documentation-criteria"
    / "references"
    / "pedagogical-marker-justification-spec-substance-keywords.txt"
)


def _load_substance_keywords() -> set[str]:
    """Load the canonical substance-keyword list. Falls back to a minimal
    hardcoded set if the spec sibling file is missing (so the audit doesn't
    silently regress)."""
    fallback = {
        "credential", "credentials", "secret", "token", "url", "link",
        "anti-pattern", "antipattern", "injection", "payload", "scanner",
        "detects", "fixture", "negative example", "intentional",
        "reference catalog", "training", "exfiltration", "vulnerable",
    }
    try:
        if _SUBSTANCE_KEYWORDS_FILE.is_file():
            words = set()
            for line in _SUBSTANCE_KEYWORDS_FILE.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    words.add(line.lower())
            if words:
                return words
    except Exception:
        pass
    return fallback


_SUBSTANCE_KEYWORDS = _load_substance_keywords()


def justification_valid(justification: str | None) -> tuple[bool, str]:
    """Per mechanism α (ADR-0030), validate a marker's inline justification.

    Returns (is_valid, reason). reason is human-readable; on invalid it explains
    which rule failed (used for the auditor-emitted finding's `what` field).

    THIS HELPER IS UNWIRED IN T007. Wiring happens in T009 (Plan §P1.4 step 5).
    Until wired, calling code continues to use the legacy two-marker check.
    """
    if not justification or not justification.strip():
        return False, "no justification provided (mechanism α requires inline justification per marker)"

    text = justification.strip()
    words = text.split()

    # Rule 1: length floor
    if len(words) < 5 or len(text) < 30:
        return False, (
            f"justification too short (rule 1): {len(words)} words / {len(text)} chars "
            f"(minimum: 5 words AND 30 chars)"
        )

    # Rule 2: banned bare-word phrase
    # Normalize: lowercase, strip punctuation
    normalized = "".join(c.lower() if c.isalnum() or c.isspace() else " " for c in text)
    tokens = [t for t in normalized.split() if t]
    content_tokens = [t for t in tokens if t not in _ARTICLES]
    if content_tokens and all(t in _BANNED_BARE_WORDS for t in content_tokens):
        return False, (
            f"justification is composed entirely of banned bare words (rule 2): "
            f"{sorted(set(content_tokens))} — must reference content type, document role, or auditor check"
        )

    # Rule 3: substance keyword presence
    text_lower = text.lower()
    if not any(kw in text_lower for kw in _SUBSTANCE_KEYWORDS):
        return False, (
            "justification lacks substance keywords (rule 3): "
            "must reference content type (e.g. 'credential patterns', 'anti-pattern'), "
            "document role (e.g. 'reference catalog', 'training fixture'), "
            "or auditor check ID (e.g. 'DE-2', 'X-9')"
        )

    return True, "ok"


def demote_one(sev: str) -> str:
    """Demote severity one notch. INFO stays INFO."""
    if sev not in SEVERITY_ORDER:
        return sev
    idx = SEVERITY_ORDER.index(sev)
    if idx + 1 >= len(SEVERITY_ORDER):
        return sev
    return SEVERITY_ORDER[idx + 1]


def parse_frontmatter(file_path: Path) -> dict[str, Any]:
    """Parse YAML frontmatter from a markdown file. Returns {} if none."""
    if not file_path.exists() or not file_path.is_file():
        return {}
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return {}

    if not content.startswith("---"):
        return {}

    # Find closing ---
    lines = content.split("\n")
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return {}

    # Parse very-minimal YAML — we only need top-level scalars and lists
    fm = {}
    current_key = None
    current_list: list[str] = []
    for line in lines[1:end_idx]:
        # List item
        m_item = re.match(r"^\s+-\s+(.*)$", line)
        if m_item and current_key:
            val = m_item.group(1).strip().strip("\"'")
            current_list.append(val)
            continue
        # New key
        m_key = re.match(r"^([a-zA-Z_\-]+)\s*:\s*(.*)$", line)
        if m_key:
            if current_key and current_list:
                fm[current_key] = current_list
                current_list = []
            current_key = m_key.group(1)
            val = m_key.group(2).strip()
            if val == "":
                # Likely a list following
                continue
            fm[current_key] = val.strip("\"'")
            current_key = None

    # Flush trailing list
    if current_key and current_list:
        fm[current_key] = current_list

    return fm


def parse_pedagogical_sections_raw(skill_path: Path) -> tuple[list[dict[str, Any]], str]:
    """Mechanism α: parse pedagogical_sections frontmatter; recognize both legacy
    bare-list form (REJECTED) and structured-dict form (validated per entry).

    Returns (entries, form) where:
      - entries: list of dicts with keys {path: str, justification: str|None,
        valid: bool, reason: str}.
      - form: one of "absent", "bare-list", "structured-dict", "malformed".

    Bare-list entries are returned with valid=False, reason="bare-list form lacks per-entry justification slot".
    Structured-dict entries are validated via justification_valid().
    """
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return [], "absent"

    try:
        content = skill_md.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return [], "absent"

    # Extract the pedagogical_sections: block from frontmatter
    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not fm_match:
        return [], "absent"

    fm_text = fm_match.group(1)
    m = re.search(
        r"^pedagogical_sections\s*:\s*(.*?)(?=^\S|\Z)",
        fm_text, re.MULTILINE | re.DOTALL,
    )
    if not m:
        return [], "absent"

    block = m.group(1)
    block_lines = [ln for ln in block.split("\n") if ln.strip()]
    if not block_lines:
        return [], "malformed"

    # Detect structured-dict form: list items each followed by indented `path:` + `justification:` keys
    # vs bare-list form: list items that are scalar strings.
    entries: list[dict[str, Any]] = []
    current_entry: dict[str, Any] | None = None
    form_signal = None  # "bare-list" or "structured-dict"

    for ln in block_lines:
        # Top-level list item: "  - <something>"
        m_item = re.match(r"^\s*-\s+(.*)$", ln)
        if m_item:
            # Flush prior entry
            if current_entry is not None:
                entries.append(current_entry)
            rest = m_item.group(1).strip()
            # Structured form starts with "path:" — bare form has just the path string
            m_path = re.match(r"^path\s*:\s*(.+)$", rest)
            if m_path:
                current_entry = {
                    "path": m_path.group(1).strip().strip("\"'"),
                    "justification": None,
                }
                form_signal = "structured-dict" if form_signal != "bare-list" else "malformed"
            else:
                current_entry = {
                    "path": rest.strip("\"'"),
                    "justification": None,
                }
                form_signal = "bare-list" if form_signal != "structured-dict" else "malformed"
            continue
        # Continuation line — indented `justification:` (only meaningful in structured-dict)
        m_just = re.match(r"^\s+(justification)\s*:\s*(.*)$", ln)
        if m_just and current_entry is not None:
            jv = m_just.group(2).strip()
            # Strip surrounding quotes if present
            if (jv.startswith('"') and jv.endswith('"')) or (jv.startswith("'") and jv.endswith("'")):
                jv = jv[1:-1]
            current_entry["justification"] = jv

    if current_entry is not None:
        entries.append(current_entry)

    if form_signal is None:
        return [], "malformed"

    # Validate each entry
    for e in entries:
        if form_signal == "bare-list":
            e["valid"] = False
            e["reason"] = "bare-list form lacks per-entry justification slot (mechanism α requires structured-dict)"
        else:
            ok, reason = justification_valid(e.get("justification"))
            e["valid"] = ok
            e["reason"] = reason if not ok else "ok"

    return entries, form_signal


def get_pedagogical_sections(skill_path: Path) -> set[str]:
    """Return set of paths declared in pedagogical_sections WITH VALID justification.

    Mechanism α: bare-list and invalid-justification entries are silently filtered
    out — callers see only validly-marked paths. The auditor surfaces the rejection
    via the marker-finding stream (see get_pedagogical_section_marker_findings).

    Returns empty set if no SKILL.md, no declaration, or all entries invalid.
    """
    entries, _form = parse_pedagogical_sections_raw(skill_path)
    return {e["path"] for e in entries if e.get("valid")}


def get_pedagogical_section_marker_findings(skill_path: Path) -> list[dict[str, Any]]:
    """Emit a MAJOR finding for each invalid pedagogical_sections entry per ADR-0030.

    Authors who declared a marker without valid justification see one finding per
    rejected declaration. The underlying findings (broken links, credential refs)
    continue to surface at their original severity because the rejection causes
    the marker to be treated as absent.
    """
    entries, form = parse_pedagogical_sections_raw(skill_path)
    findings: list[dict[str, Any]] = []
    skill_md_loc = f"{skill_path.name}/SKILL.md:pedagogical_sections"
    for e in entries:
        if e.get("valid"):
            continue
        findings.append({
            "dimension": 0,
            "severity": "MAJOR",
            "location": skill_md_loc,
            "pattern_id": "MARKER_INVALID_JUSTIFICATION",
            "what": (
                f"pedagogical_sections entry for '{e.get('path')}' rejected: {e.get('reason')}"
            ),
            "fix": (
                "Convert to structured-dict form with a content-specific justification "
                "per KB-documentation-criteria/references/pedagogical-marker-justification-spec.md"
            ),
            "marker_decision": "MARKER_REJECTED",
            "final_severity": "MAJOR",
            "marker_note": f"form={form}; reason={e.get('reason')}",
        })
    return findings


def _parse_audit_example_fence_marker(language_line: str) -> tuple[bool, str | None, str]:
    """Parse a fence opening line per mechanism α.

    Returns (is_marker_attempt, justification, parse_status):
      - is_marker_attempt: True iff language tag is exactly 'audit-example' (the
        author intended a pedagogical marker).
      - justification: the text after ' -- ' separator, or None if absent.
      - parse_status: "valid" | "no-separator" | "empty-justification" |
                      "not-audit-example".

    Per spec §3 the separator must be ' -- ' (whitespace-bounded). A bare
    'audit-example' fence (no separator) is is_marker_attempt=True with
    parse_status='no-separator'.
    """
    text = language_line.strip().lower()
    # Split on ' -- ' (whitespace-bounded)
    parts = re.split(r"\s--\s", text, maxsplit=1)
    lang = parts[0].strip()
    if lang != PEDAGOGICAL_FENCE_LANG:
        return False, None, "not-audit-example"
    if len(parts) == 1:
        return True, None, "no-separator"
    just = parts[1].strip()
    if not just:
        return True, "", "empty-justification"
    return True, just, "valid"


def is_inside_audit_example_fence(file_path: Path, line_number: int) -> bool:
    """Check whether the given line is inside a VALIDLY-JUSTIFIED ```audit-example fence.

    Per mechanism α (ADR-0030): a fence is valid only if its language line carries
    a `-- <justification>` annotation passing justification_valid(). Fences without
    the separator OR with invalid justifications are treated as if absent — finding
    inside surfaces at original severity. The auditor emits a separate marker-
    rejection finding for each invalid fence (see get_audit_example_fence_marker_findings).
    """
    if not file_path.exists() or not file_path.is_file():
        return False
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return False

    lines = content.split("\n")
    in_fence = False
    fence_is_valid = False  # only True for audit-example with valid justification

    for i, line in enumerate(lines, start=1):
        stripped = line.lstrip()
        if stripped.startswith("```"):
            if not in_fence:
                # Opening fence — parse language line
                lang_line = stripped[3:]
                is_attempt, just, status = _parse_audit_example_fence_marker(lang_line)
                if is_attempt and status == "valid":
                    ok, _ = justification_valid(just)
                    fence_is_valid = ok
                else:
                    fence_is_valid = False
                in_fence = True
            else:
                # Closing fence
                in_fence = False
                fence_is_valid = False
            if i == line_number:
                return False
            continue
        # Non-fence line
        if i == line_number:
            return in_fence and fence_is_valid

    return False


def get_audit_example_fence_marker_findings(file_path: Path) -> list[dict[str, Any]]:
    """Emit a MAJOR finding for each invalid audit-example fence per ADR-0030.

    A fence with the audit-example language tag but no valid justification
    (`-- <justification>` after the language tag) is rejected as a marker.
    """
    findings: list[dict[str, Any]] = []
    if not file_path.exists() or not file_path.is_file():
        return findings
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return findings

    lines = content.split("\n")
    for i, line in enumerate(lines, start=1):
        stripped = line.lstrip()
        if not stripped.startswith("```"):
            continue
        lang_line = stripped[3:]
        is_attempt, just, status = _parse_audit_example_fence_marker(lang_line)
        if not is_attempt:
            continue
        # Validate
        if status == "no-separator":
            reason = "bare 'audit-example' fence lacks ' -- justification' separator"
        elif status == "empty-justification":
            reason = "'audit-example -- ' fence has empty justification text"
        else:
            ok, why = justification_valid(just)
            if ok:
                continue  # valid; no finding
            reason = why

        findings.append({
            "dimension": 0,
            "severity": "MAJOR",
            "location": f"{file_path}:{i}",
            "pattern_id": "FENCE_INVALID_JUSTIFICATION",
            "what": f"audit-example fence at line {i} rejected: {reason}",
            "fix": (
                "Add ' -- <content-specific justification>' to the fence language line "
                "per KB-documentation-criteria/references/pedagogical-marker-justification-spec.md"
            ),
            "marker_decision": "MARKER_REJECTED",
            "final_severity": "MAJOR",
            "marker_note": f"fence-status={status}; reason={reason}",
        })

    return findings


def file_is_listed_pedagogical(file_path: Path, skill_path: Path,
                                 declared_sections: set[str]) -> bool:
    """Determine whether a finding's file is declared in pedagogical_sections.

    The declaration is relative to skill_path. Match against:
      - exact relative path: "references/attack-catalog.md"
      - normalized relative path with various separators
    """
    try:
        rel = file_path.relative_to(skill_path)
    except ValueError:
        return False
    rel_str = str(rel).replace("\\", "/")
    return rel_str in declared_sections


def check_anti_laundering(file_path: Path) -> list[str]:
    """Scan the file for content that overrides pedagogical claims.
    Returns list of reasons (empty if clean)."""
    reasons: list[str] = []
    if not file_path.exists() or not file_path.is_file():
        return reasons
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return reasons

    # Live credential patterns
    for pat in DANGEROUS_PATTERNS_LIVE:
        for m in pat.finditer(content):
            matched_str = m.group(0).upper()
            # Skip if string contains a well-known fake/example indicator
            if any(ind in matched_str for ind in FAKE_CREDENTIAL_INDICATORS):
                continue
            reasons.append(
                f"file contains live-looking credential string matching {pat.pattern[:40]}..."
            )
            break  # one finding per pattern is enough

    # Live attacker URLs (anything not in allowed-example list)
    for m in URL_PATTERN.finditer(content):
        host = m.group(1).lower()
        if host not in ALLOWED_EXAMPLE_HOSTS:
            # Allowed-suffix list of docs/CDN/registry/RFC-reserved hosts. Match accepts
            # both "X.<suffix>" and the bare "<suffix>" form (the original implementation
            # only matched .suffix and incorrectly flagged "github.com" as laundering).
            ALLOWED_SUFFIXES = (
                "claude.com", "anthropic.com", "microsoft.com",
                "github.com", "githubusercontent.com", "github.dev", "github.io", "python.org",
                "googleapis.com", "google.com", "amazonaws.com", "azure.com", "azurewebsites.net",
                "supabase.com", "npmjs.org", "vercel.com", "netlify.com", "heroku.com", "render.com", "fly.io",
                "cloudflare.com", "npmjs.com", "schemastore.org",
                "w3.org", "ietf.org", "rfc-editor.org",
                "docker.com", "docker.io", "redhat.com",
                "kubernetes.io", "k8s.io",
                "mozilla.org", "mdn.io", "developer.mozilla.org",
                "jsonschema.org", "json-schema.org",
                "containers.dev", "astral.sh", "renovatebot.com",
                "stripe.com",  # MCP integration provider commonly documented
                "openai.com", "atlassian.com", "slack.com",  # other MCP integration providers
                "example", "example.com", "example.org", "example.net",  # RFC 6761/2606
            )
            if not any(host == s or host.endswith("." + s) for s in ALLOWED_SUFFIXES):
                reasons.append(f"file contains live URL {host}")
                break  # one is enough

    return reasons


def declared_pedagogical_path_is_safe(skill_path: Path, declared_path: str) -> tuple[bool, str]:
    """Validate a declared pedagogical_sections entry.
    Returns (is_safe, reason_if_not).
    """
    p = skill_path / declared_path
    if not p.exists():
        return False, f"declared pedagogical file does not exist: {declared_path}"
    if not p.is_file():
        return False, f"declared pedagogical path is not a file: {declared_path}"
    # Must be a markdown content file
    if not declared_path.lower().endswith(".md"):
        return False, f"declared pedagogical file is not markdown (extension): {declared_path}"
    return True, ""


def process(skill_path: Path, findings: list[dict[str, Any]]) -> dict[str, Any]:
    """Apply triage matrix to findings. Returns processed output.

    Per mechanism α (T009 wiring): emits MAJOR findings for any rejected markers
    (invalid frontmatter pedagogical_sections entries + invalid audit-example fences
    in files that have any findings). Rejected markers do not suppress; the
    underlying finding continues to surface at original severity.
    """
    declared_sections = get_pedagogical_sections(skill_path)
    marker_findings: list[dict[str, Any]] = []

    # Mechanism α: emit rejection findings for invalid pedagogical_sections entries
    marker_findings.extend(get_pedagogical_section_marker_findings(skill_path))

    # Mechanism α: emit rejection findings for invalid audit-example fences
    # We scan only files that appear in the finding stream (avoid scanning every file).
    scanned_paths: set[Path] = set()
    for f in findings:
        loc = finding_location(f) or ""
        m = re.match(r"^(.+?):\d+$", loc)
        if not m:
            continue
        file_str = m.group(1)
        file_path = Path(file_str)
        if not file_path.is_absolute():
            file_path = skill_path / file_path
        if file_path in scanned_paths:
            continue
        scanned_paths.add(file_path)
        marker_findings.extend(get_audit_example_fence_marker_findings(file_path))

    # First: anti-laundering check on declarations themselves
    for declared in declared_sections:
        is_safe, reason = declared_pedagogical_path_is_safe(skill_path, declared)
        if not is_safe:
            marker_findings.append({
                "dimension": 0,
                "severity": "MAJOR",
                "location": f"SKILL.md:pedagogical_sections",
                "pattern_id": "ANTI_LAUNDER_DECLARATION",
                "what": reason,
                "fix": "Remove from pedagogical_sections, or fix the declaration.",
                "marker_decision": "LAUNDERING_DECLARATION",
                "final_severity": "MAJOR",
                "marker_note": "Declared pedagogical file failed structural validation.",
            })

    summary = {
        "demoted_pedagogical_full": 0,
        "demoted_marker_mismatch": 0,
        "demoted_fence_no_file": 0,
        "untouched": 0,
        "escalated_laundering": 0,
    }

    out_findings: list[dict[str, Any]] = []
    for f in findings:
        f = dict(f)  # don't mutate caller
        original_sev = f.get("severity", "INFO")

        # Parse location (use finding_location helper for backward-compat:
        # auditing-skills emits findings keyed `where`, others key `location`)
        loc = finding_location(f) or ""
        m = re.match(r"^(.+?):(\d+)$", loc)
        if not m:
            # Fall back: parse the `what:` field for references-style findings.
            # Pattern: "<source-file> links to '<target>' (line N) but the file does not exist."
            what_str = f.get("what", "")
            m_refs = re.match(
                r"^([\w./\-]+(?:\.md|\.json|\.yaml|\.yml|\.txt|\.py|\.sh|\.js|\.ts)?)\s+links to\s+'([^']+)'\s+\(line\s+(\d+)\)",
                what_str,
            )
            if m_refs:
                file_str = m_refs.group(1)
                line_str = m_refs.group(3)
            else:
                # Still no parseable file:line — cannot apply marker triage; pass through
                f["marker_decision"] = "NO_MARKER"
                f["final_severity"] = original_sev
                f["marker_note"] = "Location did not include file:line; marker triage skipped."
                out_findings.append(f)
                summary["untouched"] += 1
                continue
        else:
            file_str, line_str = m.group(1), m.group(2)
        line_number = int(line_str)

        # Resolve file path relative to skill_path or absolute
        file_path = Path(file_str)
        if not file_path.is_absolute():
            file_path = skill_path / file_path

        # Check declaration and fence
        listed = file_is_listed_pedagogical(file_path, skill_path, declared_sections)
        in_fence = is_inside_audit_example_fence(file_path, line_number)

        # Anti-laundering: if file claims pedagogical but content is operationally dangerous,
        # the finding stays at original severity with override note.
        if listed or in_fence:
            laundering_reasons = check_anti_laundering(file_path)
            if laundering_reasons:
                f["marker_decision"] = "LAUNDERING_OVERRIDE"
                f["final_severity"] = original_sev  # no demotion
                f["marker_note"] = "False pedagogical claim — " + "; ".join(laundering_reasons)
                summary["escalated_laundering"] += 1
                out_findings.append(f)
                continue

        # Apply triage matrix
        # Documentation-quality findings (broken-link, reference-illusion) vs
        # security-quality findings (credentials, pipe-to-shell, MCP poisoning):
        # the file-scope marker is meaningful for documentation findings (no
        # silent-suppression-of-credentials risk) so listed+!fence is sufficient
        # to fully demote those. For security findings, fence-wrap is still
        # required (the historical MARKER_MISMATCH behavior is retained).
        is_doc_finding = False
        what_lower = f.get("what", "").lower()
        if ("links to" in what_lower and "does not exist" in what_lower) or \
           "reference illusion" in what_lower or \
           "broken link" in what_lower:
            is_doc_finding = True

        if listed and in_fence:
            # Full marker — demote to INFO
            f["marker_decision"] = "FULL_MARKER"
            f["final_severity"] = "INFO"
            f["marker_note"] = "Full pedagogical declaration; finding demoted to INFO."
            summary["demoted_pedagogical_full"] += 1
        elif listed and is_doc_finding:
            # File-scope marker is sufficient for documentation-quality findings
            # (per justified extension; see observations OBS-EXEC-004). The
            # pedagogical_sections justification carries the substance claim
            # that these documentation paths are illustrative.
            f["marker_decision"] = "FULL_MARKER_FILE_SCOPE"
            f["final_severity"] = "INFO"
            f["marker_note"] = "File listed in pedagogical_sections; documentation-quality finding demoted to INFO."
            summary["demoted_pedagogical_full"] += 1
        elif listed and not in_fence:
            # Marker mismatch — demote one notch and add a new MAJOR finding
            f["marker_decision"] = "MARKER_MISMATCH"
            f["final_severity"] = demote_one(original_sev)
            f["marker_note"] = "Pattern in declared-pedagogical file but not inside `audit-example` fence."
            summary["demoted_marker_mismatch"] += 1
            marker_findings.append({
                "dimension": 0,
                "severity": "MAJOR",
                "location": loc,
                "pattern_id": "MARKER_MISMATCH",
                "what": "Pattern matches in declared-pedagogical file but is not inside an `audit-example` fence.",
                "fix": "Wrap the example content in a ```audit-example fence block, or remove the file from pedagogical_sections if it should be operational.",
                "marker_decision": "MARKER_FINDING",
                "final_severity": "MAJOR",
                "marker_note": "Emitted by pedagogical marker checker.",
            })
        elif not listed and in_fence:
            # Fence but no file declaration — demote one notch and emit MINOR
            f["marker_decision"] = "FENCE_NO_FILE"
            f["final_severity"] = demote_one(original_sev)
            f["marker_note"] = "Pattern inside `audit-example` fence but file not in pedagogical_sections."
            summary["demoted_fence_no_file"] += 1
            marker_findings.append({
                "dimension": 0,
                "severity": "MINOR",
                "location": loc,
                "pattern_id": "FENCE_WITHOUT_FILE_DECLARATION",
                "what": "Pattern inside `audit-example` fence but file not listed in pedagogical_sections.",
                "fix": "Add the file to pedagogical_sections in SKILL.md frontmatter.",
                "marker_decision": "MARKER_FINDING",
                "final_severity": "MINOR",
                "marker_note": "Emitted by pedagogical marker checker.",
            })
        else:
            # No marker — pass through unchanged; LLM-judge triage will run
            f["marker_decision"] = "NO_MARKER"
            f["final_severity"] = original_sev
            f["marker_note"] = "No pedagogical marker; severity unchanged for downstream triage."
            summary["untouched"] += 1

        out_findings.append(f)

    return {
        "target": str(skill_path),
        "findings": out_findings + marker_findings,
        "marker_findings": marker_findings,
        "marker_summary": summary,
    }


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: pedagogical_marker_check.py <skill-path> <findings.json>",
              file=sys.stderr)
        return 2

    skill_path = Path(sys.argv[1]).resolve()
    findings_path = sys.argv[2]

    if findings_path == "-":
        data = json.load(sys.stdin)
    else:
        with open(findings_path) as fh:
            data = json.load(fh)

    findings = data.get("findings", [])
    result = process(skill_path, findings)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
