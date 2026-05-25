# Per-Task Execution Result — T5.2

**Task:** Wire validate_adr_placement.py at run_phase_checks.py dispatch (surface b per ADR-0054)
**Status:** COMPLETED
**Phase-4 gate:** PASSED

## Files modified

- `.claude/skills/auditing-shared/scripts/run_phase_checks.py`

## What was done

### Constants block (lines 44 + 49–51)

Two new module-level constants added after the existing VALIDATOR / DISCIPLINE_CHECK declarations:

```python
ADR_PLACEMENT_VALIDATOR = SCRIPTS_DIR / "validate_adr_placement.py"

# Per ADR-0054 commitment 2: synthesize-skill output dirs are the only
# allowlisted surface for ADR placement validation.
ADR_PLACEMENT_ALLOWLIST = "output/synthesis-*/adrs/"
```

### Parallel-dispatch entry (lines 146–158)

Inserted between the frontmatter-validator dispatch block and the discipline-check block:

```python
# ADR placement validator (surface b per ADR-0054).  Runs unconditionally
# against cwd; --allowlist exempts synthesize-skill output dirs per
# ADR-0054 commitment 2.  Non-zero exit folds as BLOCKER per AC-FR-10-c.
if ADR_PLACEMENT_VALIDATOR.exists():
    tasks.append((
        "validator:adr_placement",
        [
            "python3", str(ADR_PLACEMENT_VALIDATOR),
            ".",
            "--allowlist", ADR_PLACEMENT_ALLOWLIST,
        ],
        None,
    ))
```

### Dimension rollup extension (lines 209–239)

After the existing frontmatter-validator rollup block, a second block folds
`validator:adr_placement` findings into the same `validator` dimension per Q-CC-7 Option A.
Severity values are normalised from uppercase (`"BLOCKER"`) to lowercase (`"blocker"`) so that
`dimension_rollup()`'s string comparison (`f.get("severity") == "blocker"`) fires correctly.
Error findings from a failed subprocess invocation also map directly to severity `"blocker"`.

## LOC change

+37 lines net (0 deletions). Breakdown:
- 2 constant declarations + 2 comment lines = 4 lines (constants block)
- 13 lines dispatch block
- 1 comment header + 22 lines rollup fold block = 23 lines
- 1 docstring bullet update + 2 blank lines for spacing = 7 lines

## 4-phase gate results

| Phase | Result | Detail |
|-------|--------|--------|
| Format / lint | PASS | No project formatter configured; AST parse clean |
| Build / compile | PASS | `python3 -m py_compile` exits 0 |
| Test: smoke run | PASS | Script produces JSON verdict; validator dimension shows BLOCKER from ADR placement findings; exit-code-2 semantics confirmed |
| Final gate | PASS | All phases green |

## Exit-code semantics confirmed

`run_script` already accepts exit codes 0 and 2 as valid responses from child scripts. When
`validate_adr_placement.py` exits 2 (BLOCKER findings present), the JSON output is parsed and the
findings are folded into the validator dimension with severity `"blocker"`. `dimension_rollup`
returns `"BLOCKER"`, which propagates to the overall verdict. Phase progression is blocked.

## AC coverage

- AC-FR-10-c: validator dispatch wired; non-zero exit produces BLOCKER
- AC-CC-3: findings fold into existing validator dimension (Q-CC-7 Option A)
- AC-FR-10-f: re-verification surface b wired at run_phase_checks
- AC-NFR-6-a (partial): allowlist correctly exempts output/synthesis-*/adrs/ per ADR-0054 commitment 2
