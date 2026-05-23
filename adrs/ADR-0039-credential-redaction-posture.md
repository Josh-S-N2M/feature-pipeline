---
id: ADR-0039
version: 1.0.0
status: Accepted
generated: 2026-05-23
generated_by: design-composer
supersedes: []
adrs_inherited: []
applies_to:
  - devcontainer-mcp-provisioning-r1
  - any feature that registers an MCP server requiring credentials
  - any feature that writes MCP-related log surfaces
template_format: per KB-documentation-criteria ADR template v1.0
change_summary: >-
  Establishes credential-redaction posture for the MCP surface: redact-at-source
  from the .mcp.json `env:` block and HTTP `headers:` allowlist (single source
  of truth); reject Exa-style URL-embedded credentials at config-validation time
  rather than at log time; ban argv-leaked credential patterns at config and
  runtime; secret-via-env-only invocation. Codifies OWASP MCP01 Token
  Mismanagement defense for this project.
---

# ADR-0039: Credential redaction posture — redact-at-source from `.mcp.json` env-block allowlist

## Contents

- [x] Status
- [x] Context
- [x] Decision
- [x] Decision Details
- [x] Rationale
- [x] Options Considered
- [x] Consequences
- [x] Architecture Impact
- [x] Implementation Guidance
- [x] Related Information

## Status

Accepted — 2026-05-23

## Context

OWASP MCP01 Token Mismanagement is the highest-ranked MCP risk in the synthesized corpus (claim C-0333, verified-high; verbatim OWASP guidance "Redact or mask secrets before writing to logs or telemetry" at C-0335). The PRD codifies the requirement as AC-FR-10-d (runtime log redaction), AC-NFR-2-d (security counterpart), and AC-NFR-2-a (no secret values committed). Synthesis D-0007 frames the decision as a **one-way, org-blast-radius architectural** call (RICE reach=36, impact=3.0; the top-ranked design risk by impact in this feature).

Two anti-patterns must be defended against simultaneously:

1. **Argv-leakage (E-0094).** Credentials passed via process command-line arguments leak via `/proc/<pid>/cmdline`, process-listing tools, and audit logs. The Context7 `--api-key` CLI flag (claim C-0205) and any future MCP server's positional credential argument fall into this class. **This anti-pattern cannot be fixed at the log layer alone**; it requires invocation discipline.
2. **URL-embedded credentials (E-0095).** The Exa `exaApiKey` query-parameter form (claims C-0259 / C-0260 / C-0280) leaks via browser history, HTTP proxy logs, server access logs, and any MCP client config dump that includes the URL. **This must be rejected at config-validation time, not at log-write time** — by the time the credential is in the URL, redaction is already past the leak boundary.

Per-layer Design (Q-CC-8 / synthesis §7 ADR candidate #3) correctly surfaces this as ADR-worthy. Per FR-5, the design-composer authors.

The decision is one-way because the .mcp.json `env:` block is the **single source of truth** for the redaction allowlist (synthesis D-0007 frame). Inverting that convention later would require touching every downstream consumer (log-surface wrapper, augmented `auditing-mcp` rules, KB-mcp-platform documentation).

## Decision

1. **Redact-at-source from `.mcp.json`.** The single source of truth for the credential-redaction allowlist is the union of:
   - Every env-var NAME appearing in any `${VAR}` substitution inside `.mcp.json` (every per-server `env:` block + HTTP `headers:` block values).
   - Every HTTP header NAME used to carry a credential (`Authorization`, `x-api-key`, `CONTEXT7_API_KEY` per the per-server matrix).
   The augmented `auditing-mcp` rule OP-1 enforces env-block coverage: every `${VAR}` reference must appear in the corresponding `env:` block (or be a documented header name for HTTP transports).
2. **Reject URL-embedded credentials at config-validation time.** The augmented `auditing-mcp` rule OP-9 rejects `.mcp.json` entries that put credentials in URL query parameters (specifically, the Exa `exaApiKey` form). Exa's accepted shape is `x-api-key` HTTP header only.
3. **Ban argv-leakage.** The augmented `auditing-mcp` rule OP-10 rejects `.mcp.json` `args:` arrays that contain literal credential values, `--<flag>=<credential>` patterns, or positional credential arguments. Credentials flow only via the `env:` block. The Context7 `--api-key` CLI form is rejected.
4. **Redaction implementation.** At the log-surface boundary (the writer of `.claude/runtime/mcp-events.jsonl` per ADR-0037, plus any stderr capture), apply a filter that:
   - Reads the env-var names + header names from `.mcp.json` at startup.
   - Replaces any value matching one of those env-var values with the literal `[REDACTED:<envvar-name>]`.
   - Replaces any header-value matching one of the allowlist's named header credentials with `[REDACTED:<header-name>]`.
   - Default-fails-closed: an empty allowlist (because `.mcp.json` is absent or malformed) means redact nothing AND emit a `structured_failure` record with `failure_class=process_start`.
5. **The credential never appears in committed files.** AC-NFR-2-a is enforced via `auditing-mcp` rules OP-9 / OP-10 / and (cross-layer) by Codespaces' `containerEnv` indirection via `${localEnv:VAR}` per the codespaces-design.

## Decision Details

| Item | Content |
|---|---|
| Decision | Redact-at-source from `.mcp.json` env-block + HTTP-headers allowlist; reject URL-embedded credentials at config-validation; ban argv-leakage. |
| Why now | OWASP MCP01 is the highest-ranked MCP risk; this feature is the first that registers credential-bearing MCP servers in this project. Setting the convention now prevents future MCP additions from re-litigating. |
| Why this | The `.mcp.json` `env:` block is the only artifact that already enumerates every credential the project consumes. Making it the SSOT means "add a credential" = "add to env: block" = "automatically covered by redaction." Splitting the SSOT across multiple files (e.g., a separate redaction-allowlist.json) creates drift opportunity that the augmented audit cannot catch as cheaply. |
| Known unknowns | (a) Where exactly the filter runs at the log-surface boundary — postStart wrapper vs in-process Claude Code MCP client. The cross-layer reconciliation defers to plan-author for code-site placement; the *invariant* (env-block-keyed) is fixed by this ADR. (b) Whether the redaction should also cover stdout (the spec says stdio servers should NOT log to stdout, C-0313; defensively redacting stdout is cheap). |
| Kill criteria | If a future credential class cannot be represented in the env-block-keyed allowlist (e.g., a credential composed at runtime from multiple env-vars), this ADR may need a follow-up to extend the allowlist representation. The kill criterion is "the SSOT model proves too narrow"; until then, the env-block IS the allowlist. |

## Rationale

The synthesis §3 D-0007 frame is a single-option-with-credible-no-alternatives decision: the alternatives reduce to deferral (do redaction later) or duplication (separate redaction-allowlist file). OWASP MCP01 prescribes the *property* (redact before write) but not the *mechanism*; this ADR picks the mechanism. The Velida at-instrumentation-source-by-header/env-var-name pattern (claim C-0330, verified-medium because Velida is single-vendor; principle multi-source-corroborated by OWASP MCP01) is the strongest published implementation pattern; this ADR adapts it.

The decision composes with ADR-0037 (the JSONL event surface) by reusing the same boundary: the redaction filter runs at the same write-time as the JSONL append. It composes with ADR-0040 (Serena posture) and other agent-allowlist decisions by making the consumer-mapping audit (rule OP-2) and the env-block coverage audit (rule OP-1) independent: a new agent gaining a credential-bearing server tool does NOT widen the allowlist; the allowlist is keyed on what `.mcp.json` declares, not on what agents consume.

## Options Considered

### Option 1: Redact-at-source from `.mcp.json` env-block (SSOT) (selected)

**Pros:** Single source of truth; "add a credential" = "add to env-block" = "covered by redaction"; the augmented `auditing-mcp` can audit env-block coverage as a single rule (OP-1).

**Cons:** Requires `auditing-mcp` to grow rule OP-9 / OP-10 to defend against the two anti-patterns that the env-block alone cannot prevent (URL-embedded and argv-leaked).

### Option 2: Separate redaction-allowlist.json file

**Pros:** Decouples redaction-allowlist concerns from MCP server registration.

**Cons:** Two files to keep in sync; drift opportunity; augmented `auditing-mcp` must audit consistency between the two; no real benefit over Option 1 for our scale (7 servers).

### Option 3: Redact-at-log-only via regex on credential shapes

**Pros:** No `.mcp.json` schema dependency.

**Cons:** Credential-shape regex (`AKIA...`, `ghp_...`, `sk_live_...`) misses custom env-var values (a CONTEXT7_API_KEY might be a UUID and not match any well-known shape). False negatives = silent credential leak — the worst class of failure.

### Option 4: Defer redaction to a future feature

**Pros:** Minimum-touch for this feature.

**Cons:** Violates AC-FR-10-d / AC-NFR-2-d; OWASP MCP01 is unmitigated; the new `.claude/runtime/mcp-events.jsonl` surface ships unredacted. Unacceptable.

## Consequences

### Positive Consequences

- A single artifact (`.mcp.json`) determines the redaction surface; adding a credential to a new MCP server automatically extends redaction coverage.
- The augmented `auditing-mcp` skill becomes the safety-net (OP-1 env-block coverage, OP-9 URL-credential rejection, OP-10 argv-leakage rejection, OP-6 runtime-log redaction integrity) — operator-runnable as a single audit gate.
- The `mcp-events.jsonl` surface (ADR-0037) is safe-by-design: writes go through the redaction filter.
- Defense-in-depth is explicit: argv-leakage defended at config; URL-credential defended at config; log-write defended at the wrapper.

### Negative Consequences

- Three augmented-`auditing-mcp` rules (OP-1, OP-9, OP-10) must be maintained in lockstep with `.mcp.json` evolution.
- Codespaces' `postStart.sh` (the JSONL writer per codespaces-design) must consume the env-block allowlist at startup; this introduces a `.mcp.json` parse step in postStart whose error path must be considered (default-fail-closed: empty allowlist + `structured_failure` event).
- Future credential classes that need to be composed from multiple env-vars at runtime are not directly representable; an ADR follow-up would be needed.

### Neutral Consequences

- The Exa CLI `--header` form (when supported by Claude Code per OI-CS-5 verify-at-execution) is the operationally-preferred shape. The fallback (header inside `.mcp.json` HTTP block) satisfies this ADR equally.
- The Codespaces secrets surface is unaffected; the credential value still flows Codespaces → `containerEnv` → `${VAR}` substitution → `.mcp.json` → MCP server. Only the log-write boundary changes.

## Architecture Impact

1. **Layers affected.** Claude Code / Project Filesystem (owns `.mcp.json` and the `auditing-mcp` augmentation), Dev Environment / Codespaces (owns the postStart-time consumer of the allowlist).
2. **Components that change.**
   - `.mcp.json` (NEW) — declares the per-server env: block; the **redaction SSOT**.
   - `auditing-mcp` augmentation rules OP-1 (env-block coverage), OP-6 (runtime-log redaction integrity), OP-9 (URL-credential rejection), OP-10 (argv-leakage rejection).
   - `.devcontainer/postStart.sh` (NEW) — consumes the allowlist before any write to `mcp-events.jsonl` or stderr; applies the filter.
   - `KB-mcp-platform/references/auth-and-redaction.md` (NEW) — documents the SSOT, the two anti-patterns, and the OWASP MCP01 reference.
   - `KB-mcp-design/references/patterns-and-anti-patterns.md` (NEW) — names argv-leakage and URL-credential as anti-patterns.
3. **New dependencies introduced.** None at the runtime level. `jq` (already in base image per codebase-analysis) is used to parse the `.mcp.json` env-block at postStart.
4. **Architectural constraints added.**
   - The `.mcp.json` `env:` block is reserved for credential names; non-credential env vars (e.g., feature flags) MUST live in the per-server `env:` block too (the allowlist is over-inclusive — better to redact a non-credential by accident than to leak a credential).
   - The Context7 `--api-key` CLI form is project-wide-banned.
   - The Exa `exaApiKey` URL query-parameter form is project-wide-banned.

## Implementation Guidance

**Where the filter runs.** The redaction filter wraps writes to `.claude/runtime/mcp-events.jsonl` and to stderr that flows into operator-visible surfaces. The exact code-site (postStart wrapper vs in-process Claude Code) is a plan-author concern; the *invariant* — env-block-keyed allowlist consumed at write-time — is fixed here. The cross-layer reconciliation defers to plan-author for the code-site choice; the augmented `auditing-mcp` rule OP-6 audits the **result** (no credential shape in mcp-events.jsonl) regardless of where the filter runs.

**Default-fail-closed.** If the allowlist is empty (because `.mcp.json` is absent or fails to parse), the postStart writer MUST emit a `structured_failure` record with `failure_class=process_start` and `message_redacted="cannot load .mcp.json; allowlist empty; refusing to write events"`. The lifecycle proceeds (warn-and-continue per codespaces-design Q-CS-3) but the operator is informed.

**Format.** Replacement format is `[REDACTED:<envvar-name>]` (literal string substitution); the augmented `auditing-mcp` rule OP-6 greps for credential shapes (AWS keys, JWT shapes, etc.) AND for any 16-byte+ entropy-looking string that wasn't redacted, as an additional safety net.

**No procedural detail in the ADR.** Sequencing of `.mcp.json` env-block authoring, allowlist consumer wiring, and audit-rule activation lives in the Plan.

## Related Information

- Related ADRs: ADR-0037 (mcp-events.jsonl event surface — consumes the same boundary), ADR-0007 (codebase-memory-mcp fallback — its registration entry must follow this redaction posture if it grows credentials), ADR-0038 (codebase-analysis schema — independent contract).
- Referenced specs / docs: synthesis.md §3 D-0007, §5 Operational Discipline Brief, §7 ADR candidate #3; cc-design.md `.mcp.json` design section + auditing-mcp augmentation plan (OP-1/OP-6/OP-9/OP-10); codespaces-design.md Secrets and Config section. T-007-mcp-operational.md F4 (OWASP MCP01), F4.2 (Velida at-source pattern).
- Issues / PRs: (none directly; resolves the OWASP MCP01 design concern raised in synthesis §7).
- Related KBs: KB-mcp-platform (`auth-and-redaction.md` reference home), KB-mcp-design (`patterns-and-anti-patterns.md` anti-pattern home), `auditing-mcp` (OP-1/6/9/10 audit rules).
