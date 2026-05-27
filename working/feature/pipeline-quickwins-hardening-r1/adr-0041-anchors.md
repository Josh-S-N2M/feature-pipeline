# ADR-0041 Row Anchors — T0.3 Capture

Captured 2026-05-26 for T1.5 reference. Source file:
`adrs/ADR-0041-install-mechanism-hybrid.md`

## Verification

L1 check: `grep -c "DEPRECATED INVOCATION FORM" adrs/ADR-0041-install-mechanism-hybrid.md` returns **2**.

Both annotations are present and load-bearing for T1.5's deprecated-row recognition logic.

---

## Row 70 — Serena (line 70)

**Table position:** invocation-form table, second data row (after header at line 68 and blank at line 69)

**Server column value:** `Serena`

**Mechanism column value:** `uvx --from` (Python; uv-managed; ephemeral)

**Form column value (verbatim):**

```
`uvx --from "git+https://github.com/oraios/serena@${SERENA_REF}" serena start-mcp-server` `[DEPRECATED INVOCATION FORM — actual installed via uv-tool; runtime invocation is `serena start-mcp-server` from PATH after `uv tool install`; see postCreate.sh:82 + .mcp.json:28-31. Annotation added 2026-05-26 by pipeline-quickwins-hardening-r1 Architecture Audit cycle 1 finding I-AA-003. Decision content of ADR-0041 unchanged; prose-only annotation per ADR-0005 hygiene.]`
```

**Annotation token (for T1.5 regex/string-match):** `[DEPRECATED INVOCATION FORM`

**Annotation opens at:** the backtick-delimited second span on line 70, immediately following the original Form text.

---

## Row 71 — mcp-openapi-schema (line 71)

**Table position:** invocation-form table, third data row

**Server column value:** `mcp-openapi-schema`

**Mechanism column value:** `npx -y` (Node ephemeral via npm cache)

**Form column value (verbatim):**

```
`npx -y "mcp-openapi-schema@${MCP_OPENAPI_SCHEMA_VERSION}" <spec-path>` `[DEPRECATED INVOCATION FORM — server removed from .mcp.json and postCreate.sh on 2026-05-24 per the MCP postmortem; the prescription row is preserved here for audit-trail per ADR-0005 append-only discipline but no longer corresponds to a live install. Annotation added 2026-05-26 by pipeline-quickwins-hardening-r1 Architecture Audit cycle 1 finding I-AA-003 (the row-71 sibling to row-70 Serena's annotation, missed by the design-composer's initial pass and caught at commit-prep time). Decision content of ADR-0041 unchanged; prose-only annotation per ADR-0005 hygiene.]`
```

**Annotation token (for T1.5 regex/string-match):** `[DEPRECATED INVOCATION FORM`

**Annotation opens at:** the backtick-delimited second span on line 71, immediately following the original Form text.

---

## Notes for T1.5

- The string `[DEPRECATED INVOCATION FORM` is the unique prefix shared by both annotations. T1.5's deprecated-row recognition logic can match on this prefix to identify rows that must be skipped by the OP-11 audit rule.
- Row 70's annotation records a form change (invocation mechanism changed; server still live).
- Row 71's annotation records a server removal (server removed 2026-05-24; row preserved for audit trail per ADR-0005 append-only discipline).
- Both annotations were added on 2026-05-26 by pipeline-quickwins-hardening-r1 Architecture Audit cycle 1 finding I-AA-003.
- The table header sits at line 68; row 70 is the first data row (Serena); row 71 is the second data row (mcp-openapi-schema). Line numbers are stable as of this capture — T1.5 should match by annotation token, not by line number, for robustness.
