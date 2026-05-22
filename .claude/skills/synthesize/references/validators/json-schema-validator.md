# JSON Schema Validator Helper

> Shared validator contract consumed by every Layer A QA point in the pipeline. Implementation lives in the orchestrator skill body (the synthesize SKILL.md) and is invoked by every phase agent that writes a phase artifact.

## Contract

```
validate(artifact_path: string, schema_path: string) -> {
  ok: boolean,
  errors: list[{ path: string, message: string }] | null
}
```

- **`artifact_path`** — absolute path to the JSON file to validate (e.g., `working/synthesis/<run-id>/01-claims.json`).
- **`schema_path`** — absolute path to the schema file (e.g., a claim-schema JSON under references/schemas/).
- **Return** — `ok: true` with `errors: null` when valid; `ok: false` with non-empty errors array otherwise.
- **Error path format** — JSON Pointer (e.g., `/claims/3/source_uri` for the source_uri of the 4th claim).

## Behavior on validation failure

Per Design §8 row "schema-violation handling":

1. **First failure** — caller retries the offending operation once with the schema embedded in the prompt to the LLM. (For per-source Extractor: re-invoke the agent for that source. For Synthesizer: re-emit the violating section.)
2. **Second failure** — caller surfaces an `AskUserQuestion` describing the validation errors and offering: edit-and-retry, skip-this-source, abort-run.

The validator helper itself is **silent on success and verbose on failure**. It does not log success cases.

## Layer A QA mechanism mapping

This helper realizes the **Layer A schema validators** mechanism from the work plan's adopted-QA-mechanisms table. Coverage by phase artifact:

| Artifact | Schema | Caller |
|---|---|---|
| `00-manifest.json` | `manifest.schema.json` | orchestrator (Confirmation Gate, task-07) |
| `01-claims-<source-slug>.json` (per-source) | `claim.schema.json` (validates each item in `claims` array) | orchestrator (per-source loop, task-06) |
| `01-claims.json` (merged) | `claim.schema.json` | orchestrator (after merge, task-06) |
| `02-graph.json` | `entity-graph.schema.json` | orchestrator (after Grapher, task-10) |
| `03-critique.json` | `critique.schema.json` | orchestrator (after Critic, task-12) |
| `04-decision-frames.json` | `decision-frame.schema.json` | orchestrator (after Framer, task-17) |
| `05-substrate-map.json` | `substrate-mapping.schema.json` | orchestrator + synth-substrate (task-18; the agent ALSO runs B-3opt validator before its own write) |

## Hook promotion (task-24, conditional)

If the hook-availability probe (task-23) confirms `PostToolUse` support, the Layer A validator is promoted to a `PostToolUse` hook matching `Write` on `working/synthesis/<run-id>/0[1-5]-*.json` (per Design §4.7 first row). The in-skill caller path remains as fallback. See task-24.

## Implementation reference

A reference implementation in Python using the `jsonschema` library:

```python
import json
import jsonschema

def validate(artifact_path: str, schema_path: str) -> dict:
    with open(schema_path) as f:
        schema = json.load(f)
    with open(artifact_path) as f:
        instance = json.load(f)
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)
    if not errors:
        return {"ok": True, "errors": None}
    return {
        "ok": False,
        "errors": [
            {
                "path": "/" + "/".join(str(p) for p in e.absolute_path),
                "message": e.message
            }
            for e in errors
        ]
    }
```

Production implementation may use any equivalent library; the contract is what matters.
