---
id: GATE-6-HARD-GATE-CONTRACT-devcontainer-mcp-provisioning-r1
doc_type: gate-6-contract
status: declared
generated: 2026-05-23
generated_by: orchestrator (parent recipe-feature-pipeline; Phase 5 T5.1 drive)
feature_slug: devcontainer-mcp-provisioning-r1
adrs_referenced: [ADR-0037, ADR-0039, ADR-0042, ADR-0043]
---

# Gate-6 Hard-Gate Contract — `auditing-mcp` Augmented Audit

Per ADR-0043 (Gate-4 OI-3 closure; user disposition "hard gate"). The augmented `auditing-mcp` audit's Gate-6 invocation is **gate-blocking severity**: any BLOCKER finding halts the orchestrator at Gate 6. No operator-bypass is permitted.

User rationale (verbatim, preserved per ADR-0043):

> *"I agree hard gate. MCPs can cause a lot of problems if they are not stable and the system fails silently or the devcontainer and docker fail."*

## Contract for `test-phase-validator-author` (downstream consumer)

The phase-validator at PV-5 (Rollout) consumes this contract. The audit invocation:

```bash
python .claude/skills/auditing-mcp/scripts/audit_mcp.py <path-to-.mcp.json> --with-runtime
```

### Inputs read by the audit

| Input | Source | Purpose |
|---|---|---|
| `.mcp.json` | repo root | 7-server inventory + transport + auth shapes |
| 36 agent files | `.claude/agents/*.md` | per-agent `mcp__*` allowlist verification (OP-2, OP-3) |
| `.claude/runtime/mcp-events.jsonl` | per-Codespace | runtime probe records (OP-6 redaction; OP-7 schema) |
| `.devcontainer/devcontainer.json` | repo root | env-block + lifecycle hooks |
| `.devcontainer/postCreate.sh` | repo root | OP-5 lifecycle + OP-8 GitNexus install discipline |
| `.devcontainer/postStart.sh` | repo root | OP-5 lifecycle + OP-7 schema emission |
| `.devcontainer/lib/log-mcp-event.sh` | repo root | OP-6 redaction discipline |
| `.devcontainer/versions.env` | repo root | OP-8 GitNexus pin |
| `.claude/skills/auditing-mcp/SKILL.md` | repo root | family frontmatter (ADR-0042 graduation verify) |
| `.claude/skills/auditing-cc-configs/SKILL.md` | repo root | sub-skill family pruning (ADR-0042 step 3 verify) |
| `KB-codebase-research`, `discovery-codebase-researcher.md` | repo root | OP-4 primary/fallback prose preservation |

### Audit dimensions

The augmented audit dispatches the 10 OP rules in addition to the pre-existing `validate_mcp_config.py`, `scan_mcp_secrets.py`, and `check_toxic_combinations.py`. Per Phase 4 T4.3 + the post-Phase-5 dispatch wiring in `audit_mcp.py`:

| Rule | Severity threshold | Description |
|---|---|---|
| Pre-existing: `validate_mcp_config.py` | BLOCKER on schema violation | Validates `.mcp.json` schema (transport/command/url/headers). Recognizes `transport: "http"` per Phase 5 T5.4 fix. |
| Pre-existing: `scan_mcp_secrets.py` | BLOCKER on literal credential | Scans for credential-shaped strings in `.mcp.json`. |
| Pre-existing: `check_toxic_combinations.py` | BLOCKER on toxic pair | Checks for toxic capability combinations (filesystem + web, etc.). |
| OP-1 env-block coverage | BLOCKER on literal credential in headers/env | ADR-0039 |
| OP-2 consumer-mapping | MAJOR on missing/extra mcp__ entries | Blueprint v3.0.2 Sub-Agents table |
| OP-3 zero-mcp invariant | BLOCKER on mcp__ in untouched agent | C-0445 |
| OP-4 primary/fallback prose | MAJOR on missing prose | ADR-0007 v2.2.0 |
| OP-5 lifecycle completeness | MAJOR on count mismatch | ADR-0037 (5 install_complete + 7 readiness_probe) |
| OP-6 runtime-log redaction | BLOCKER on credential in JSONL | ADR-0039 default-fail-closed |
| OP-7 events schema | BLOCKER on invalid JSON; MAJOR on missing fields | ADR-0037 schema |
| OP-8 GitNexus install + consumers | BLOCKER on missing pin/env-var/consumer | Cycle-3 F2 + AC-CS-9 |
| OP-9 URL-query credential | BLOCKER on URL-query credential | Cycle-3 + ADR-0039 |
| OP-10 argv-leakage | BLOCKER on argv credential | ADR-0039 |

### Gate-6 hard-gate semantics (per ADR-0043)

- **Exit 0 from `audit_mcp.py`**: zero BLOCKER findings → orchestrator proceeds past Gate 6.
- **Exit 1 from `audit_mcp.py`**: at least one BLOCKER finding → orchestrator HALTS at Gate 6.
- **No operator-bypass.** The hard gate does not honor `--force` flags or similar overrides.
- **Remediation path**: read the audit report's findings; resolve each BLOCKER per the rule's `fix:` field; re-run `audit_mcp.py`; orchestrator resumes Gate 6 once exit 0 is observed.

### Live exercise — Phase 5 T5.4 result (2026-05-23T22:00 UTC)

**Clean repo state**: `audit_mcp.py .mcp.json` returns exit 0 with 0 BLOCKER + 3 MINOR (MC-3 known-publishers advisory; non-gating). 10 OP rules dispatched cleanly.

**Seeded-BLOCKER simulation** (cycle-3 D-3.2-completion + Phase 5 T5.4 exercise): temporarily added `?apiKey=sk-TESTPOISON1234567890abcd` to context7's URL. Result:
- OP-9 detected the violation: `[BLOCKER] credential-shaped query parameter: apiKey (server: context7)`
- `audit_mcp.py` exit code: **1** (HALT)
- Hard-gate verdict: HALT

**cleanup_required executed**: `.mcp.json` restored from backup; grep confirms zero `TESTPOISON` residual; final `audit_mcp.py` run returns 0 BLOCKER. Per T5.4 contract — seeded credential is NEVER committed.

## Contract for downstream phase-validator-author

When `test-phase-validator-author` re-runs at the next pipeline iteration (or in a future feature's phase-validators), it MUST:

1. Reference this contract in PV-5's hard-gate criteria (PV-5.C-HARDGATE + PV-5.C-HARDGATE-EXERCISE per phase-validators.md v1.0.1).
2. Specify the invocation exactly: `python .claude/skills/auditing-mcp/scripts/audit_mcp.py <path-to-.mcp.json>` (add `--with-runtime` for postStart-fired probes).
3. Specify the exit-code interpretation: `0 = PROCEED, 1 = HALT, 2 = usage error`.
4. Specify cleanup_required for any seeded-BLOCKER exercise: ALWAYS restore `.mcp.json` from backup before committing.

The phase-validators.md v1.0.1 already declares PV-5.C-HARDGATE and PV-5.C-HARDGATE-EXERCISE in line with this contract. This document is the canonical contract; phase-validators.md is the per-phase consumer.

## Cross-references

- **ADR-0043** — hard gate decision + user verbatim rationale
- **ADR-0042** — auditing-mcp family graduation (the audit IS its own family-coordinator)
- **ADR-0037** — mcp-events.jsonl event surface
- **ADR-0039** — credential redaction posture
- **phase-validators.md v1.0.1** — PV-5.C-HARDGATE + PV-5.C-HARDGATE-EXERCISE
- **plan-v1.md T5.1** — this contract is the deliverable
- **plan-v1.md T5.4** — the live exercise that verified the contract works
- **acceptance-tests.md AT-HG** — the shared triplet test (AC-CC-5 + AC-FR-11-c + AC-NFR-2-c) that AT-HG verifies via this contract
