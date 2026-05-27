# postCreate.sh Anchor Record — T0.4

Captured: 2026-05-26  
Source: `.devcontainer/postCreate.sh`  
Purpose: Stable insertion-point reference for T2.2 (FR-4a static-shape check block).

## Lines 195–202 verbatim

| Line | Content |
|------|---------|
| 195 | `install_serena              \|\| emit_degraded_banner "serena"              "<no fallback>"` |
| 196 | `install_actionlint_mcp      \|\| emit_degraded_banner "actionlint-mcp"      "<no fallback>"` |
| 197 | `install_terraform_mcp       \|\| emit_degraded_banner "terraform-mcp"       "<no fallback>"` |
| 198 | `install_gitnexus            \|\| emit_degraded_banner "gitnexus"            "<no fallback>"` |
| 199 | *(blank line)* |
| 200 | `echo "[postCreate] running gitnexus setup + analyze pre-warm..."` |
| 201 | `gitnexus_post_install_warm  \|\| emit_degraded_banner "gitnexus" "<post-install warm failed; runtime fallback path unchanged>"` |
| 202 | *(blank line)* |

## Anchor confirmation

- **Line 197** corresponds to `install_terraform_mcp || emit_degraded_banner ...` — confirmed.
- **Line 198** corresponds to `install_gitnexus || emit_degraded_banner ...` — confirmed.
- **FR-4a insertion point**: BETWEEN line 197 and line 198. The gap is unobstructed (no other statement intervenes).
- **gitnexus_post_install_warm** sits at line 201, after install_gitnexus at line 198.

## Three-position non-collision (T2.2 + T2.3 planning)

```
Line 197: install_terraform_mcp || emit_degraded_banner ...
          ^^^ INSERT FR-4a static-shape check block HERE (T2.2)
          ^^^ INSERT Q-CS-1b staleness banner HERE (T2.3, adjacent to FR-4a, before install_gitnexus)
Line 198: install_gitnexus || emit_degraded_banner ...
Line 200: echo "[postCreate] running gitnexus setup + analyze pre-warm..."
Line 201: gitnexus_post_install_warm || emit_degraded_banner ...
```

The user-confirmed three-position non-collision holds:
1. FR-4a static check — before `install_gitnexus` (T2.2 insertion point after line 197)
2. `install_gitnexus` — line 198 (unchanged)
3. `gitnexus_post_install_warm` — line 201, after install completes (T2.2's anchor per Plan)
