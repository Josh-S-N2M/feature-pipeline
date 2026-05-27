---
id: ADR-0067
title: Remove security checks from the auditing-* skill family
status: Accepted
date: 2026-05-27
supersedes: []
superseded_by: null
---

# ADR-0067 — Remove security checks from the auditing-* skill family

## Status

Accepted (2026-05-27).

## Context

The auditing-cc-configs project audit (and its component auditing-* skills) included a set of security-flavored checks inherited from generic Claude Code configuration auditing guidance:

- `scan_security.py` (OWASP Agentic AI Top 10 indicators in skills)
- `scan_memory_secrets.py` (literal credentials in auto-memory and subagent-memory files)
- `scan_settings_secrets.py` (literal credentials in settings.json env blocks)
- `scan_mcp_secrets.py` (literal credentials in MCP server configs)
- `check_toxic_combinations.py` (toxic-capability combinations across MCP servers)
- `audit_op9_url_credential_rejection.py` (URL-query credential anti-pattern)
- `scan_subagent_body.py` SA-3 (wildcard shell tool grant) and SA-4 (prompt-injection / bypassPermissions-with-dangerous-tools)
- `validate_hooks_config.py` CVE-2025-59536-class check (SessionStart hook with network egress)
- `validate_mcp_config.py` MC-4 (download-and-execute risk)
- `validate_output_styles.py` ST-8 (safety-override patterns in output-style bodies)
- `analyze_hook_script.py` SECURITY_PATTERNS line scan
- `verdict_compute.has_security_block()` (escalates any `is_security_critical: True` BLOCKER to a SECURITY-BLOCK verdict that overrides the project score)

Empirically, during the direct-counterfactual-repair session on 2026-05-27, these checks were observed to:

1. Produce findings at rates that overwhelmed signal-to-noise (e.g., 2 SA-4 findings flagged the project's own `issue-capture-author.md` subagent — which was authored intentionally with the relevant safety prompts — as a critical-severity prompt-injection vector).
2. Create persistent SECURITY-BLOCK verdicts that masked the project's true audit posture (score 0.0/100 throughout the direct-counterfactual-repair work, despite the substantive finding count dropping from 153 to 46).
3. Generate workaround pressure rather than actionable fixes: the user reported "noisy and a lot of false positives and work arounds."

This project is a single-developer research vehicle for AI-driven feature pipelines, not a multi-tenant production system. Its threat model is dominated by *the user's own intentions* (the only operator with write access is the user) and by *external supply-chain risks* on MCP packages (which are pinned and reviewed at install time per ADR-0041). The generic OWASP-aligned checks were calibrated for a different threat model — one where untrusted contributors author subagents, where credentials might leak across multi-developer settings, and where the auditing layer is a continuous-integration gate.

## Decision

Disable all security-flavored checks in the auditing-* skill family. The implementation is the smallest reversible mutation: each security-scanning script's `main()` is replaced with a stub that emits `{"findings": []}` and exits 0, and each inline security-emission site in non-scanning audit scripts is replaced with a one-line comment citing this ADR. The functions and patterns remain on disk so the decision is reversible via `git revert` of the corresponding commits.

The `SECURITY-BLOCK` verdict band is functionally removed: `has_security_block()` always returns `False`, so the project verdict is determined entirely by the score-band mapping (`PASS≥95 / PASS-WITH-MINOR-FIXES 85–94 / NEEDS-WORK 70–84 / FAIL<70`).

The `is_security_critical` field remains in the data schema and is honored by `triage_with_judge.py` if any future emission produces it — it just has no caller. This preserves forward compatibility if security checks are re-enabled later.

## Consequences

**Intended (positive):**
- Audit verdicts now reflect substantive findings, not pattern-matched security alarms.
- The project score will accurately surface PASS/FAIL bands as discipline and reference-rot issues are addressed.
- Re-baselining the audit produces a clean signal for tracking real progress.

**Accepted (negative):**
- The audit no longer detects literal credentials in settings.json, MCP configs, or memory files. The user accepts responsibility for not committing real credentials; the `.gitignore` and the env-block indirection pattern (per ADR-0039) provide the primary mitigation.
- The audit no longer flags SessionStart hooks that perform network egress (the CVE-2025-59536 class). The user controls all hooks in this project; this risk class does not apply to a single-developer setup.
- The audit no longer flags subagent bodies that instruct bypass of approval prompts. The user authored those instructions deliberately for the `issue-capture-author` subagent's documented behavior.
- The audit no longer flags toxic capability combinations across MCP servers. The five remaining MCP servers (serena, context7, exa, actionlint-mcp, terraform-mcp) are all from known publishers with reviewed capabilities.

**Reversibility:** This ADR's mechanism is a stub-replacement, not a deletion. Each disabled scanner's full implementation remains in `git log`. To re-enable security checks, restore the previous `main()` body from git history.

## Rationale (decision class)

- **Class:** Reversible mechanism change with documented threat-model justification.
- **Blast radius:** Audit output only; no runtime, no published interface.
- **Cost of being wrong:** Bounded — re-enable via git revert. If a real security incident occurs that the disabled check would have caught, the cost is the incident plus the cost of the revert.

## Alternatives considered

1. **Tune severities downward** (BLOCKER → MINOR for all security findings): rejected because the noise was not the severity — it was the volume and the false-positive rate. Lowering severity preserves the noise.
2. **Add a per-check feature flag** (e.g., `--no-security`): rejected because the user's stated goal is to remove the noise, not to add a flag they would always set.
3. **Filter security findings at the report layer** (e.g., grep out `is_security_critical: True` before rendering): rejected because the scanners would still run and consume audit time, and the SECURITY-BLOCK verdict would still escalate.
4. **Delete the scanner files entirely**: rejected as less reversible. The stub-replacement pattern keeps the implementation discoverable for future reversal.

## Cross-references

- The direct-counterfactual-repair Issue: `Issues/direct-counterfactual-repair/analysis.md`
- ADR-0039 (env-block credential indirection — the primary mitigation that remains in place)
- ADR-0041 (MCP install-mechanism-hybrid — supply-chain mitigation that remains in place)
- ADR-0066 (gitnexus removal — sibling architectural cleanup from the same session)
