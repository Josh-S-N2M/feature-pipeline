---
name: auditing-mcp
description: >-
  Audits Claude Code MCP (Model Context Protocol) server configurations in
  settings.json mcpServers blocks or .mcp.json files. ALWAYS invoke when
  reviewing, auditing, evaluating, scoring, vetting, fixing, or critiquing
  MCP server configs, when triaging "my MCP server isn't working," when
  evaluating MCP supply-chain risk, or when running --with-runtime to
  probe live servers. Validates server config schema, transport choice,
  credential handling, toxic capability combinations (filesystem + web,
  database + network), and (optionally) live tool descriptions. Report-only.
allowed-tools: Read Grep Glob Bash(python3 *)
family: auditing-mcp
pedagogical_sections:
  - path: references/mcp-spec.md
    justification: "MCP spec reference; contains anti-pattern examples of unsafe MCP configurations the auditor flags"
  - path: references/toxic-combinations.md
    justification: "Toxic-combinations reference; documents MCP server combinations the auditor flags (anti-pattern catalog)"
  - path: references/anti-patterns.md
    justification: "MCP anti-pattern reference catalog documenting what the auditing-mcp scanner detects as findings"
  - path: references/common-failures.md
    justification: "MCP common-failures catalog with negative-example fixtures the auditing-mcp scanners flag"
  - path: examples/bad-mcp-annotated.md
    justification: "Bad-MCP annotated negative-example fixture demonstrating tool-poisoning and other anti-patterns"
---

# Auditing Claude Code MCP Servers

Audits MCP (Model Context Protocol) server configurations. MCP servers extend Claude Code with custom tools — filesystem access, database queries, search APIs, and so on. They are the highest-risk extensibility surface because each server brings its own tool definitions that load into Claude's context.

This skill is the **family coordinator** for the `auditing-mcp` family — graduated from the `auditing-cc-configs` family per ADR-0042 (cycle-3 Gate-4 OI-2 closure, devcontainer-mcp-provisioning-r1). The graduation was made on failure-domain-distance grounds: MCP failures (silent silent-failure, devcontainer/docker breakage, supply-chain compromise) are operationally distinct from `.claude/`-config correctness, which is what `auditing-cc-configs` covers. Shared rubric, weights, thresholds, and triage utilities still live in `auditing-shared` per ADR-0031 (`auditing-shared` is the cross-family utility home; `auditing-mcp` now consumes it as an independent family-coordinator).

## Sub-skill family

This coordinator is the first member of its own family. The sub-skill list is currently empty — reserved for future MCP-audit sub-skills (e.g., a per-server-deep-dive sub-skill, a runtime-only audit sub-skill). When sub-skills are added (in future features), they'll be enumerated here and dispatched per the established `auditing-cc-configs` pattern.

It writes one file: an audit report. It does not modify configs or contact servers (except in `--with-runtime` mode).

## The audit loop

1. **Locate the target.** Either:
   - A `mcpServers` block in settings.json
   - A standalone `.mcp.json` file
   - A path to a project containing one or both

2. **Run deterministic checks:**

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/audit_mcp.py <path>
   ```

3. **Optionally** invoke runtime probing:

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/audit_mcp.py <path> --with-runtime
   ```

   Runtime mode connects to each server, lists its tools, and applies the toxic-combinations check against actual tool descriptions. Off by default since it runs untrusted code (the server itself).

4. **Apply verification step.** Especially important for MCP — tool descriptions can contain prompt-injection payloads.

5. **Run pedagogical-marker prefilter** if applicable.

6. **Compute verdict and write report.**

## Routing table — dimensions

| # | Dimension | Reference |
|---|---|---|
| 1 | Config schema validity | `references/mcp-spec.md` |
| 2 | Transport choice | `references/mcp-spec.md` |
| 3 | Credential handling | `references/mcp-spec.md` |
| 4 | Server-name uniqueness | `references/mcp-spec.md` |
| 5 | Toxic capability combinations | `references/toxic-combinations.md` |
| 6 | Tool-description safety | `references/toxic-combinations.md` |
| 7 | Supply-chain provenance | `references/mcp-spec.md` |
| 8 | Anti-pattern absence | `references/anti-patterns.md` |
| 9 | Cross-scope interactions | `references/common-failures.md` |
| 10 | Runtime behavior (--with-runtime only) | `references/toxic-combinations.md` |

## OP-rule routing table

Each OP-rule is a discrete, scriptable invariant the auditor enforces. The table maps each rule to its implementation script, reference document, severity when a finding is raised, and a one-line rationale.

| Rule | Name / Title | Script | Reference doc | Severity on finding | Rationale |
|---|---|---|---|---|---|
| OP-11 | `.mcp.json` ↔ ADR-0041 invocation-form parity | `scripts/audit_op11_adr_parity.py` | `references/adr-parity.md` | BLOCKER | Preserve ADR-prescribed invocation forms in the live `.mcp.json`; deprecated rows annotated `[DEPRECATED INVOCATION FORM]` are skipped. |

## Critical: MCP servers run untrusted code

A `mcpServers` entry specifies a command Claude Code will spawn. The first MCP-server install of a new server is effectively trusting the supplier. The auditor's recommendations should always include: read the server source, check the publisher's reputation, prefer `npx -y <official-package>` over arbitrary commands.

## Runtime mode (--with-runtime)

Off by default. When enabled, the auditor:

1. Reads the server config.
2. Spawns the server.
3. Sends the MCP `tools/list` request.
4. Receives the tool list.
5. Scans tool descriptions for prompt-injection patterns and toxic combinations.
6. Shuts down the server.

Runtime mode requires the user to opt in (via the flag). The auditor warns explicitly that this spawns the configured commands.

## Severity meanings (v2)

- **BLOCKER** — config won't load, exposes credentials, or has toxic combination.
- **MAJOR** — works but degrades security.
- **MINOR** — deviates from best practice.
- **NIT** — taste.

PASS 95+, PASS-WITH-MINOR-FIXES 85–94, NEEDS-WORK 70–84, FAIL <70. SECURITY-BLOCK on confirmed CRITICAL.

## Calibration examples

- [`examples/good-mcp-annotated.md`](examples/good-mcp-annotated.md) — well-formed config scoring 95+
- [`examples/bad-mcp-annotated.md`](examples/bad-mcp-annotated.md) — toxic combination + leaked credential, SECURITY-BLOCK

## Scope

In scope: `mcpServers` blocks in settings.json at any scope, `.mcp.json` files.

Not in scope: hooks (route to `auditing-hooks`), permissions (route to `auditing-settings`), CLAUDE.md, subagents, output styles.

## Report-only contract

This skill never modifies configs. The runtime probe (when enabled) only sends MCP protocol requests; it does not call non-list tools.
