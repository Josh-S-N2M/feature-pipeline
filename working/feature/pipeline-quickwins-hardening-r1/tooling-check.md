# Tool Availability — pipeline-quickwins-hardening-r1

Recorded: 2026-05-26
Satisfies: PV-0.C5

## Summary

| Tool | Path | Version | Status | Fallback |
|------|------|---------|--------|----------|
| actionlint | — | — | ABSENT | `mcp__actionlint-mcp__lint_workflow` MCP tool (Plan T3.3 contract permits this fallback when binary is missing) |
| jq | /usr/bin/jq | 1.6 | PRESENT | none required |
| python3 | /usr/local/bin/python3 | 3.11.13 | PRESENT (≥ 3.10) | none required |
| bash | /usr/bin/bash | 5.2.15(1)-release (x86_64-pc-linux-gnu) | PRESENT | none required |
| mktemp | /usr/bin/mktemp | coreutils 9.1 | PRESENT | none required |
| gh | /usr/bin/gh | 2.92.0 (2026-04-28) | PRESENT | none required |
| npx | /usr/local/share/nvm/current/bin/npx | 10.8.2 | PRESENT | none required |

## Notes

- **actionlint** binary is not on PATH. Plan T3.3 explicitly permits falling back to the `mcp__actionlint-mcp__lint_workflow` MCP tool in this case; no blocker for downstream tasks.
- **python3** at 3.11.13 satisfies the ≥ 3.10 minimum required by `audit_op11_adr_parity.py` and `verdict_findings_parity.py`.
- **jq**, **bash**, **mktemp** are all GNU coreutils-sourced and present at expected paths.
- **gh** CLI is present and current; will support Plan T4.7 (PR open) and T5.2 (post-merge workflow trigger).
- **npx** is present via nvm at version 10.8.2; supports `npx gitnexus analyze` and other npx-invoked tooling.
