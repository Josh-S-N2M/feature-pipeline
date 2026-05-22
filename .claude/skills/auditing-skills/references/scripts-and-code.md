# Scripts and Code (Dimension 7)

How bundled scripts in `scripts/` should be written. Use this when scoring dimension 7. N/A for skills that don't include scripts — score 10 and note in the report.

## Contents

- The "solve, don't punt" rule
- Voodoo constants
- Path conventions
- Dependency declarations
- Execution intent: run vs read
- Script-vs-instruction balance
- Specific findings to look for

## The "solve, don't punt" rule

Scripts should handle their own error conditions, not raise unhandled exceptions for Claude to figure out.

Bad — punts to Claude:

```python
def process_file(path):
    return open(path).read()
```

Good — handles the predictable failure modes:

```python
def process_file(path):
    """Process a file, creating it if it doesn't exist."""
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        print(f"File {path} not found, creating default")
        with open(path, "w") as f:
            f.write("")
        return ""
    except PermissionError:
        print(f"Cannot access {path}, using default")
        return ""
```

The principle: any error condition that's predictable should be handled in the script, not surface as an exception that the agent has to interpret. Genuinely unexpected errors are fine to raise.

**Finding:** Scripts that fail on the first edge case (missing file, missing key, malformed input) without any handling: MAJOR. Scripts that handle some cases but raise opaque exceptions on others: MINOR.

## Voodoo constants

Configuration parameters should be justified. Magic numbers without explanation force the agent to guess what's safe to change.

Bad:

```python
TIMEOUT = 47
RETRIES = 5
```

Good:

```python
# HTTP requests typically complete within 30 seconds.
# Longer timeout accounts for slow connections and large payloads.
REQUEST_TIMEOUT = 30

# Three retries balances reliability vs speed.
# Most intermittent failures resolve by the second retry.
MAX_RETRIES = 3
```

**Finding:** Numeric constants without inline justification: MINOR per occurrence (cap at MAJOR if there are 5+).

## Path conventions

Always use forward slashes, never backslashes. Forward slashes work on every platform; backslashes break on Unix.

```python
# Good
config_path = "config/defaults.json"

# Bad
config_path = "config\\defaults.json"
```

In SKILL.md instructions, the same rule. `${CLAUDE_SKILL_DIR}/scripts/<name>.py` is correct; `${CLAUDE_SKILL_DIR}\scripts\<name>.py` is broken on Linux/Mac.

**Finding:** Backslash paths anywhere (script or instruction): MINOR per occurrence.

## Dependency declarations

If the skill's scripts need packages (`pandas`, `requests`, etc.), state this explicitly in `SKILL.md` and verify the package is available in the runtime environment.

Bad — assumes installation:

```markdown
Use the pdf library to process the file.
```

Good — explicit:

```markdown
Required: `pip install pypdf` (PyPI). Then:

    from pypdf import PdfReader
    reader = PdfReader("file.pdf")
```

For environments without network access (Claude API, some sandboxed environments), declare what's available rather than what to install.

**Finding:** Script imports a non-stdlib package with no install instruction in SKILL.md: MAJOR (script will fail at runtime). Install instruction is present but uses outdated package name: MINOR.

## Execution intent: run vs read

Make clear in SKILL.md whether Claude should *execute* a script or *read* it as reference.

```markdown
Execute (most common):
    Run scripts/analyze.py to extract fields.

Read as reference (for complex algorithms):
    See scripts/analyze.py for the field-extraction algorithm.
```

If unclear, Claude often does the wrong thing — reading a script that should have been run, or trying to execute a Python file that's actually a reference module.

**Finding:** Script referenced in SKILL.md without clear "run" or "read" verb: MINOR. Script that needs execution but is described in a way that suggests reading: MAJOR.

## Script-vs-instruction balance

When deciding whether to put logic in a script vs in SKILL.md instructions:

- **Deterministic, repetitive, fragile work** → script. (YAML parsing, file existence checks, regex matching, format conversions.)
- **Judgment, synthesis, decisions based on context** → instructions. (Choosing what to recommend, adapting to user intent.)

A script that asks Claude to make 20 judgment calls is the wrong shape (the script can't make judgments — it should call out to a model). An instruction that asks Claude to "carefully count occurrences and apply the formula" is also the wrong shape (a script would do this exactly, every time).

**Finding:** Skill embeds a long deterministic procedure in instructions when a script would do: MINOR (over time, MAJOR if the procedure is buggy in practice). Script tries to encode judgment ("if the user seems to want X..."): MAJOR.

## Specific findings to look for

### BLOCKER findings

- Script with hardcoded path that will fail in any user's environment.
- Script that performs destructive action with no confirmation, dry-run flag, or rollback.

### MAJOR findings

- Scripts that punt obvious failure modes to the agent.
- Imports of non-stdlib packages with no install instruction.
- Script execution intent unclear in SKILL.md.
- Long deterministic procedure embedded in instructions instead of a script.
- Backslash paths (Windows-style) in any file.

### MINOR findings

- Magic constants without inline justification.
- Single-occurrence backslash path.
- Verbose error messages that bury the actionable line.
- Script (e.g. `scripts/<name>.py`) accepts arguments but their format is undocumented in SKILL.md.

### NIT findings

- Script lacks docstring.
- Script imports unused modules.
- Inconsistent variable naming.

## What "good" looks like

A scripts directory earns full marks when:

- Each script handles its predictable error modes.
- Constants are justified with comments.
- Required packages are declared in SKILL.md.
- Each script's execution vs read intent is unambiguous.
- Forward slashes throughout.
- The boundary between script work and judgment work is clean.
