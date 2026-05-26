---
id: cicd-design-pipeline-quickwins-hardening-r1
doc_type: per_layer_design_subsection
layer: cicd
version: 0.3.0
status: draft
feature_slug: pipeline-quickwins-hardening-r1
derived_from: working/feature/pipeline-quickwins-hardening-r1/prd-v1.md
synthesis_source: working/feature/pipeline-quickwins-hardening-r1/synthesis.md
codebase_analysis: working/feature/pipeline-quickwins-hardening-r1/codebase-analysis.json
companion_data: cicd-dependencies.json
generated: 2026-05-26T00:00:00Z
revised: 2026-05-26T00:00:00Z
generated_by: design-cicd (fallback-authored by main agent — see note in §Lint findings)
revision_history:
  - version: 0.1.0
    note: initial fallback authorship by main agent (design-cicd MCP-schema validation error)
  - version: 0.2.0
    note: revised per Gate-0/Gate-1 reviewer findings — fixed jq escape (I-DR-001 critical); reconciled AC-FR-5-a/b/c PRD-literal (I-DR-002); added pre-merge unauthenticated-CLI validation (I-DR-003); clarified four-vs-six server terminology (I-DR-004); tightened D-0010 kill-criterion + added pre-merge latency gate (I-DR-005); anchored ADR-0041 glob with .md (I-DR-006); noted workflow-level permission scope (I-DR-007); added Plan task contract for SHA resolution (I-DR-008); added actionlint Plan task (I-DR-009); added pipefail comment to jq (I-DR-010); added Q-CICD-9
  - version: 0.3.0
    note: extended scope to cover FR-4c — CI wiring for the FR-4b GitNexus grammar-skip calibration script. Added new section "FR-4c — Calibration CI wiring" specifying weekly cron + on-change-to-versions.env + workflow_dispatch triggers, a second workflow file at `.github/workflows/gitnexus-grammar-skip-calibration.yml` running the codespaces-owned calibration script inside the devcontainer image. Extended FR-5 section to acknowledge two-workflow convention. Extended SHA-pinning Plan-task contract to cover the new workflow. Added Q-CICD-10 (stale-calibration banner — Codespaces-side concern) and Q-CICD-11 (ADR-0037 event-surface schema extension for `calibration_result` event type — cross-layer Codespaces+CI/CD concern). NFR alignment: NFR-4 committed under 2 min p95 for the calibration job; NFR-7 preserved (no new secrets); NFR-13 surfaced as Q-CICD-11.
---

# CI/CD Layer Design — pipeline-quickwins-hardening-r1

This is the per-layer CI/CD subsection of the Blueprint, authored per the discipline in KB-github-actions-design and the platform facts in KB-github-actions-platform. The layer's scope for this feature is **two** new GitHub Actions workflows. The first (FR-5) is a connectivity smoke test that asserts every server entry in `.mcp.json` is in the `connected` state after a fresh devcontainer provision, and fails any PR that breaks that invariant. The second (FR-4c — added in v0.3.0 after the Codespaces designer split FR-4 into three sub-mechanisms) is the CI wiring that drives the maintainer-only GitNexus grammar-skip behavioral-calibration script (FR-4b, owned by the Codespaces layer) on a schedule and on every change to `versions.env`, so the script does not degrade into an unobserved maintainer-only shell file. Both workflows are the project's first two under `.github/workflows/` — there is no prior precedent for runner choice, permission scopes, SHA-pinning, or path filters here, so the shape this document fixes becomes the project's convention until a future feature deliberately revises it. The convention this layer establishes is therefore **two-workflow**, not one-workflow, and the SHA-pinning + diagnostic + permissions discipline applies symmetrically to both.

## Layer Responsibility Scope

The CI/CD layer owns, for this feature:

- **Two** new workflow files under `.github/workflows/`:
  - `.github/workflows/mcp-connectivity-smoke.yml` (FR-5).
  - `.github/workflows/gitnexus-grammar-skip-calibration.yml` (FR-4c — added in v0.3.0).
- The trigger surface for each (which paths cause the FR-5 smoke to run on a pull request; which schedule + path + dispatch combination drives the FR-4c calibration).
- The runner choice and execution-environment shape for each (devcontainer image vs clean Ubuntu runner; D-0007 resolved for FR-5; same posture adopted for FR-4c for the same fidelity reasons).
- The MCP health-check invocation for FR-5 (the `claude --bare -p ... --output-format stream-json | jq` path the research note T-002 establishes; not `claude mcp list`).
- The invocation of the Codespaces-owned calibration script for FR-4c (the `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` shell entrypoint).
- The permission scopes the `GITHUB_TOKEN` is granted in each workflow (least-privilege; both are CI checks, neither is a deploy).
- The on-failure diagnostic shape (FR-6 honored: name the mechanism, the offending server / grammar, the rule violated, the remedial hint) in both workflows.
- SHA-pinning discipline for any third-party action used in either workflow.

The CI/CD layer does NOT own, but consumes:

- `.mcp.json` itself — design-claude-code owns; the FR-5 workflow reads it as the artifact under test.
- The devcontainer image — design-codespaces owns; both workflows run inside it (per D-0007).
- ADR-0041's invocation taxonomy — design-claude-code owns; the workflow doesn't read it directly (the parity audit per FR-3 is a separate skill-side check).
- The Claude Code CLI itself — design-codespaces owns its provisioning (it is already installed in the devcontainer via the `claude-code` Feature).
- The `auditing-mcp` skill — design-claude-code owns its OP-rules; the workflow could optionally invoke the skill as a secondary smoke step, but D-0007 does not call for that and FR-5's named contract is purely the `claude mcp list`-equivalent connectivity check.
- The FR-4b calibration script at `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` — design-codespaces owns. The FR-4c workflow invokes it; the script itself, its Signal-1/2/3 logic, its `mcp-events.jsonl` emission, and the `versions.env` pin it reads are all Codespaces-layer concerns.
- The FR-4a per-rebuild static check inside `postCreate.sh` — design-codespaces owns. CI does not interact with it; it is mentioned here only to disambiguate FR-4's three sub-mechanisms.
- The `mcp-events.jsonl` event surface defined by ADR-0037 — design-claude-code owns the schema; the FR-4b script writes to it; CI verifies (post-run) that the script wrote an event but does not author the schema itself. The potential need for a `calibration_result` event type that ADR-0037 may not yet name is surfaced as Q-CICD-11.

A note on server-count terminology used throughout this document. `postCreate.sh` installs the four OSS-local servers (Serena, actionlint-mcp, terraform-mcp, GitNexus) and runs auth probes against the two HTTP servers (Context7, Exa); the `.mcp.json` registers all six (the four OSS-local + the two HTTP). The smoke verifies all six initialize to `status: connected`. Where this document says "OSS-local servers" it means the four; where it says "MCP servers in `.mcp.json`" or "six MCP servers" it means the registered set the smoke exercises.

This layer adds no environments, no secrets, no reusable workflows, no composite actions, no concurrency group, no OIDC federation, and no deploy step. The workflow is a single-purpose CI check.

## Decisions resolved

### D-0007 (synthesis decision; this layer owns) — path triggers, execution environment, MCP health-check invocation

The PRD's U-5 deferred the trigger globs and execution-environment choice to this designer. The synthesis (`§3 D-0007`) recommended a specific shape and that shape is adopted here essentially as-recommended, with one small refinement.

**Path triggers (`on.pull_request.paths`):**

```yaml
on:
  pull_request:
    paths:
      - '.mcp.json'
      - '.devcontainer/**'
      - 'adrs/ADR-0041-*.md'
      - '.claude/skills/auditing-mcp/**'
```

Rationale for each glob:

- `.mcp.json` — the artifact being smoked. Any change here, by definition, can break connectivity.
- `.devcontainer/**` — the install surface for the four OSS-local servers (Serena, actionlint-mcp, terraform-mcp, GitNexus) per the codebase analysis, and the auth-probe surface for the two HTTP servers (Context7, Exa). A change to `postCreate.sh`, `versions.env`, the Dockerfile, `devcontainer.json`, or the `lib/log-mcp-event.sh` helper can silently break a server install path or an auth probe. `**` covers all of them in one glob — narrower than `.devcontainer/*.sh` would miss the `lib/` and `versions.env` paths.
- `adrs/ADR-0041-*.md` — the install-mechanism taxonomy ADR. An ADR edit alone cannot break connectivity (it's a doc), but an ADR edit that prescribes a new invocation form is almost always paired with a `.mcp.json` or `postCreate.sh` change that DOES break things. Including this glob makes the workflow run when the prescription changes, which is the right time to surface drift even if the realization-side change is in a sibling commit. Narrowed to the file pattern, not all of `adrs/**`, because most ADR edits are unrelated and would create CI noise. The `.md` anchor defends against accidental triggers from `.bak`, `.orig`, or editor-swap files that the wildcard alone would catch.
- `.claude/skills/auditing-mcp/**` — the audit skill that consumes the same `.mcp.json` from the FR-3 parity-rule side. A change to the audit logic itself can mask a real connectivity drift, so a workflow run is warranted.

Globs deliberately excluded: `.claude/skills/auditing-mcp/scripts/audit_op*.py` is covered by the `**` above (do not need to call out individual files); `.github/workflows/**` is not included because the workflow editing itself is not a connectivity question — adding it would create a self-trigger loop for cosmetic edits; `CLAUDE.md` and `AGENTS.md` (the same file under symlink) are not included because they document, they don't configure.

**Execution environment: the project's devcontainer image, not `ubuntu-latest`.**

The synthesis (D-0007 §"Why the devcontainer image rather than clean ubuntu-latest") makes the argument: the smoke's value is environment-fidelity. The whole reason FR-5 exists is to catch drift that the existing devcontainer provisioning let through — running on a different host than developers run on would test a parallel universe, not the failure mode the feature names. The cost is image-build time on every trigger; the NFR-4 five-minute budget is the ceiling that bounds this.

The mechanism for "run inside the devcontainer image" on a GitHub-hosted Ubuntu runner is the `devcontainers/ci@v0.3` action (or the SHA-pinned form of it — see lint findings). This action builds the devcontainer (or pulls a pre-built image if one is configured), executes the workflow's command inside it, and tears down. It is the canonical GitHub-Actions-side equivalent of "run in the dev environment."

Alternative considered and rejected: a clean `ubuntu-latest` runner with the `claude` CLI installed inline via the Anthropic-published `claude-code` Feature equivalent. Faster cold-start, no image build, but it would test connectivity against a different filesystem layout, different binaries on PATH, different env-var shape, different secrets surface, different Node/Python versions. The mismatch is exactly the class of bug FR-5 exists to surface; running outside the devcontainer would mask it.

**MCP health-check invocation: the SDK-event path, not `claude mcp list`.**

This is the load-bearing decision. T-002's research note (Findings 1-3 + Synthesis §3 and §5) establishes that the canonical Claude Code docs are silent on `claude mcp list`'s exit-code and stdout-format contracts. Sibling commands in the same CLI family (`claude auth status`, `claude daemon status`, `claude ultrareview`) document their exit codes explicitly; the absence-by-contrast for `claude mcp list` is structurally meaningful. A workflow that depends on `claude mcp list` returning non-zero on a disconnected server is depending on undocumented behavior — exactly the failure mode the FR-5 risk row names ("misreading the contract").

The documented, contract-bearing path is the Agent SDK `system/init` event, reachable from the CLI via `claude --bare -p "<noop>" --output-format stream-json`. That event carries `mcp_servers[]`, an array of `{name, status, ...}` records. The status field uses the canonical enum `"connected" | "failed" | "needs-auth" | "pending" | "disabled"` (defined in the TypeScript and Python Agent SDK docs at `https://code.claude.com/docs/en/agent-sdk/typescript` and `.../agent-sdk/python`, and recommended for filtering at `https://code.claude.com/docs/en/agent-sdk/mcp` "Error handling"). The MCP page itself shows the canonical filter: `mcp_servers.filter((s) => s.status !== "connected")`.

The workflow's pass/fail logic is therefore:

```bash
claude --bare -p "noop" --output-format stream-json \
  | jq -c 'select(.type=="system" and .subtype=="init") | .mcp_servers[] | select(.status != "connected")'
```

If `jq` emits any non-empty line, at least one server is non-connected. The exit-code from the pipeline is then forced to non-zero via a small wrapper that captures `jq`'s output and tests it. The matched records are surfaced in the GitHub job summary so the maintainer sees server name and status without re-running the workflow (FR-6).

The noop prompt is literally `"noop"` (or any short string the model will not respond to with anything substantive). The `--bare` flag keeps startup deterministic and suppresses session metadata that would inflate the stream-json output. The MCP initialization runs before the model is invoked in any meaningful way, so the `system/init` event is emitted within the first few hundred milliseconds; the workflow terminates the pipe as soon as the event is captured. The model token cost is one short request — acceptable given NFR-4's five-minute budget covers it many times over.

**Pre-merge validation of the unauthenticated-CLI assumption.** This design asserts that `claude --bare -p "noop" --output-format stream-json` emits the `system/init` event with a populated `mcp_servers[]` array regardless of credential state — i.e., that MCP initialization completes before any model-side authentication is required. T-002's research note carries this claim with a caveat; the Agent SDK docs describe the event surface but do not explicitly contract that `system/init` is emitted in the unauthenticated state. To prevent the workflow shipping on an unverified assumption, the Plan must include a **pre-merge validation task**: before merging the workflow, an operator runs `claude --bare -p "noop" --output-format stream-json` inside the project's devcontainer in the same unauthenticated state CI will use (no `ANTHROPIC_API_KEY` in env, no logged-in user session) and confirms the captured output contains a JSON line with `.type == "system" && .subtype == "init" && (.mcp_servers | length) > 0`. If the event is not emitted in that state, the design's fallback is to introduce a read-only `ANTHROPIC_API_KEY` repo secret scoped to this workflow (with a documented and explicit deviation from NFR-7, captured in the Blueprint), so that the smoke can proceed to the point where `system/init` is reachable. The decision tree: (1) validation passes — workflow ships as designed; (2) validation fails — file a Blueprint addendum that adds the auth secret + the NFR-7 deviation. Q-CICD-8 is upgraded from "future monitoring" to "Plan task" and Q-CICD-9 captures the AC-revision fallback above.

**Version-pinning of the Claude Code CLI.** T-002's Finding 7 notes that specific MCP-related behaviors pin to specific Claude Code versions (e.g., v2.1.121 changed initial-connection retry behavior). The Agent SDK status enum is the stable contract across the current 2.1.x family, but pinning is the hardening. The devcontainer already pins the Claude Code Feature (the `claude-code` devcontainer Feature is the install path); the workflow inherits whatever version the image was built with. No separate workflow-side pin is required as long as the image's `claude-code` Feature continues to specify an exact version. If the devcontainer ever changes to `version: latest`, that decision becomes a CI-fragility concern — flagged as Q-CICD-1.

**PRD-literal reconciliation for AC-FR-5-a/b/c.** The PRD's acceptance criteria AC-FR-5-a/b/c literally name `claude mcp list` as the invocation. This design substitutes `claude --bare -p "noop" --output-format stream-json | jq` per the synthesis decision D-0007, which is itself grounded in T-002's research note and the verified critiques t002-C-0001 (no documented exit-code contract for `claude mcp list`), t002-C-0002 (no documented stdout-format contract), and t002-C-0008 (the SDK `system/init.mcp_servers[]` surface is the only documented contract-bearing path). The substitution preserves the *behavioral* intent of AC-FR-5-a/b/c — "the smoke fails when any server in `.mcp.json` is not connected after a fresh devcontainer provision" — while replacing the underlying mechanism with one that has a documented contract. The smoke's pass/fail evaluation maps cleanly: AC-FR-5-a ("smoke runs on PR with `.mcp.json` change") is satisfied by the path-trigger config; AC-FR-5-b ("smoke fails the PR check when a server is disconnected") is satisfied by the `jq` filter returning a non-empty result and the step exiting 1; AC-FR-5-c ("smoke names the offending server in actionable terms") is satisfied by the `$GITHUB_STEP_SUMMARY` FR-6 diagnostic block. The design-composer should rewrite AC-FR-5-a/b/c in the Blueprint to reference the substitute invocation rather than `claude mcp list`, so the AC text and the implementation match. This reconciliation also invalidates PRD Assumption A-3 ("`claude mcp list` is available in the devcontainer and its exit code reflects connectivity"); the substitute invocation has its own availability assumption — the Claude Code CLI being on PATH in the devcontainer image — which is already pinned via the `claude-code` Feature (a Codespaces-layer responsibility, not a new design-CI/CD obligation). The composer's options are: (a) rewrite AC-FR-5-a/b/c in the Blueprint to reflect the substitute invocation and supersede A-3 with an explicit note about the CLI-on-PATH assumption, or (b) flag the AC-revision as Q-CICD-9 for the maintainer to resolve in the Acceptance Test Authoring stage. This design recommends (a); Q-CICD-9 captures (b).

### D-0010 (concrete latency thresholds) — partially this layer's surface

The synthesis (D-0010) defers latency thresholds to the named designers. CI/CD owns NFR-4's "well under five minutes" budget. The target this design commits to:

- **Workflow runtime, p95: under 4 minutes** on the standard GitHub-hosted `ubuntu-latest` runner (2-core, 7GB RAM). This includes: runner provisioning (~30 s), devcontainer image build (estimated 2-3 minutes from a cold cache; faster if prebuilds land separately), `claude --bare -p` invocation (target: under 30 s for the `system/init` event capture; the model is not actually invoked for substantive work), `jq` parse and job-summary emission (negligible). Headroom of one minute against the NFR-4 ceiling.
- **Workflow runtime, p50: under 3 minutes** under typical conditions.
- **Measurement methodology:** track wall-clock `start-time` to `end-time`. Because the thresholds are *estimates* from KB-cited typical devcontainer build times rather than measurements from this project's specific image, the design adopts a two-stage verification posture:
  - **Pre-merge:** the Plan author adds a task to dispatch the workflow on a draft branch via `workflow_dispatch` three times consecutively (cold-cache, warm-cache, and a third run after a no-op rebuild of the devcontainer image) and records the wall-clock for each. Pass criteria: all three runs complete within NFR-4's 5-minute ceiling; at least one run completes within the 4-minute p95 target. Fail criteria (any one suffices): any of the three runs exceeds 5 minutes, or two of three exceed the 4-minute target. On fail, the Plan does not merge until either the devcontainer is sped up or the workflow shape is revised. This shifts the discovery surface from "after the carve-out ships" to "before it ships."
  - **Post-merge:** track the first ten runs after merge. The PRD's Kill-criterion is tightened from "if NFR-4's 5-minute ceiling is exceeded consistently" to **"if any of the first three post-merge runs exceeds the NFR-4 5-minute ceiling, revert the workflow immediately"** — do not wait for a ten-run trend. The pre-merge gate above should make this rare, but the tightened kill-criterion is the belt to the pre-merge braces.
  - If post-merge p95 trends toward 4 minutes without breaching 5, the canonical mitigation is a Codespaces-side prebuild — flagged as Q-CICD-2 because the image-caching surface is a Codespaces-layer concern, not CI/CD's to author.

## FR-5 — MCP connectivity smoke (workflow specification)

This section specifies the FR-5 PR-time connectivity smoke unchanged from v0.2.0. FR-4c's specification follows in the next sibling section.

### File location and identifier

- **Path:** `.github/workflows/mcp-connectivity-smoke.yml`
- **Display name** (the `name:` key in the workflow YAML): `MCP Connectivity Smoke`
- **Job identifier** (key under `jobs:`): `smoke`

The name and job-id are short, descriptive, and lowercase-with-hyphens — consistent with the project's general naming posture even though there is no prior `.github/workflows/` convention to follow.

### Trigger configuration

```yaml
on:
  pull_request:
    paths:
      - '.mcp.json'
      - '.devcontainer/**'
      - 'adrs/ADR-0041-*.md'
      - '.claude/skills/auditing-mcp/**'
  workflow_dispatch: {}
```

Notes:

- The `pull_request` event (not `pull_request_target`) is correct here. `pull_request_target` runs in the context of the base branch with broader token scopes and is reserved for cases where untrusted PR code must not gain access to secrets. This workflow needs no secrets (the smoke uses only the devcontainer image and the `claude` CLI), and the natural blast-radius for an attacker who landed a malicious `.mcp.json` would be the workflow's own runner, not the project's secrets. `pull_request` is therefore both safer and correct.
- `workflow_dispatch: {}` is added so a maintainer can manually re-run the smoke without opening a no-op PR. The empty `{}` is intentional — no inputs needed, but the key must be present for the trigger to be valid.
- No `push:` trigger to `main` is added. The PRD's FR-5 is a PR-time check; the merge-time equivalent would be valuable but is out-of-scope for this carve-out and is flagged as Q-CICD-3.
- No `schedule:` trigger. A nightly smoke that catches upstream MCP server outages would be valuable but is out-of-scope and Q-CICD-4 captures it.

### Permissions

```yaml
permissions:
  contents: read
```

The workflow reads the PR's tree (to access `.mcp.json` and the devcontainer config), does not write back to the repo, does not comment on PRs (the diagnostic surfaces in the job summary, not in a PR comment — the maintainer already sees the failed check), does not deploy anything, does not interact with any external cloud, does not use OIDC. `contents: read` is the canonical minimum and matches KB-github-actions-platform non-negotiable #2 (least privilege).

The `permissions:` block is declared at the workflow level (not the job level) because the workflow has a single job; the workflow-level declaration is simpler to audit (one block applies to everything) and there is no per-job permission divergence to express. If a future feature splits this workflow into multiple jobs with different scope needs, the convention would shift to per-job blocks at that point.

Future expansions worth flagging: if a follow-on feature wants the workflow to post a sticky PR comment listing the disconnected servers, that would require `pull-requests: write`. Adding it now without a need would violate least-privilege; the diagnostic flows through the job summary today.

### Concurrency

Not set. Concurrency groups are mandatory for deploy workflows (KB non-negotiable #5) to prevent racing two deploys to the same environment. This is a CI check that has no side effects on shared state — two PR runs against the same branch can safely run in parallel. Setting `concurrency` would only matter if the maintainer wanted PR runs to cancel earlier in-flight runs for the same PR, which is a maintainer-ergonomics call rather than a correctness concern. Default behavior (run-to-completion) is adopted; a future tightening could add `concurrency: { group: smoke-${{ github.head_ref }}, cancel-in-progress: true }` if maintainer ergonomics calls for it. Flagged as Q-CICD-5 if it ever becomes relevant.

### Job and step shape

```yaml
jobs:
  smoke:
    name: MCP connectivity (devcontainer-image fidelity)
    runs-on: ubuntu-latest
    timeout-minutes: 8

    steps:
      - name: Checkout PR head
        uses: actions/checkout@<SHA>  # v4.x — see SHA-pinning table below

      - name: Build and run devcontainer
        uses: devcontainers/ci@<SHA>  # v0.3.x — see SHA-pinning table below
        with:
          runCmd: |
            set -euo pipefail

            echo "::group::claude mcp connectivity check (SDK-event path)"

            # Capture stream-json output; tee to a file so we can both surface
            # raw output and parse it deterministically.
            OUTPUT="$(mktemp)"
            trap 'rm -f "$OUTPUT"' EXIT

            claude --bare -p "noop" --output-format stream-json > "$OUTPUT" || {
              echo "::error::claude --bare -p exited non-zero; cannot evaluate MCP state. Check Claude Code install and credentials in the devcontainer image."
              cat "$OUTPUT" || true
              exit 2
            }

            # Filter for the system/init event's mcp_servers[] where status != "connected".
            # Per Anthropic Agent SDK docs (https://code.claude.com/docs/en/agent-sdk/mcp,
            # "Error handling"), status != "connected" is the canonical disconnected filter.
            # Note on `|| true`: under `set -e`, jq exits 1 when its filter matches nothing —
            # which for us is the PASS signal (no disconnected servers). The `|| true` keeps
            # `set -e` from terminating the step on that benign exit code; we evaluate BAD's
            # emptiness explicitly below.
            BAD="$(jq -c '
              select(.type == "system" and .subtype == "init")
              | .mcp_servers[]?
              | select(.status != "connected")
              | {name: .name, status: .status}
            ' < "$OUTPUT" || true)"

            echo "::endgroup::"

            if [ -z "$BAD" ]; then
              echo "All MCP servers reported status=connected."
              {
                echo "## MCP Connectivity Smoke — PASS"
                echo ""
                echo "All servers in \`.mcp.json\` reported \`status: connected\` from the Agent SDK \`system/init\` event."
              } >> "$GITHUB_STEP_SUMMARY"
              exit 0
            fi

            # FR-6 actionable diagnostic.
            {
              echo "## MCP Connectivity Smoke — FAIL"
              echo ""
              echo "**Mechanism:** FR-5 MCP connectivity smoke (workflow \`mcp-connectivity-smoke.yml\`)."
              echo "**Offending artifact:** \`.mcp.json\` (or a devcontainer install step that provisions one of its servers)."
              echo "**Rule violated:** every server in \`.mcp.json\` must report \`status: connected\` after a fresh devcontainer provision."
              echo "**Servers not connected:**"
              echo ""
              echo '```json'
              printf '%s\n' "$BAD"
              echo '```'
              echo ""
              echo "**Remedial hint:** rebuild the devcontainer locally, run \`claude --bare -p noop --output-format stream-json | jq\` and inspect the \`system/init\` event for the named servers. Check the matching install step in \`.devcontainer/postCreate.sh\` and the corresponding \`.mcp.json\` entry. If the failure is upstream (the server's package or endpoint is broken), re-pin or open a fix upstream."
            } >> "$GITHUB_STEP_SUMMARY"

            exit 1
```

Notes on the step shape:

- **`timeout-minutes: 8`** is the per-job timeout (KB-github-actions-platform review checklist: set timeout on long jobs to prevent runaway billing). Eight minutes is the NFR-4 ceiling (5 min target) plus a small headroom for image-build outliers.
- **`set -euo pipefail`** in the shell block — matches the existing `postCreate.sh` posture per the codebase analysis (the project's shell scripts use this; CI shell blocks should too).
- **No `\${{ github.event.* }}` interpolation into `run:` blocks.** KB-github-actions-platform non-negotiable #3 (script injection). The `runCmd:` value above is a static literal heredoc; no PR-author-controlled string is interpolated. The `BAD` variable is filled from `jq`'s parse of the SDK's structured output, not from any PR-author string.
- **`trap 'rm -f "$OUTPUT"' EXIT`** is a small hygiene measure so the temp file is cleaned on any exit path. Not strictly necessary on an ephemeral runner, but cheap and right.
- **`exit 1` for the connectivity-fail case; `exit 2` for the tool-error case.** The two-code distinction matches the existing `auditing-mcp` script convention per the codebase analysis (exit 0 / 1 / 2 for no-finding / blocking-finding / internal-error). The workflow logs distinguish the two in human-readable form for the maintainer.
- **`::group::` and `::endgroup::`** are GitHub Actions log-grouping directives (workflow commands documented at `docs.github.com/en/actions/learn-github-actions/workflow-commands-for-github-actions`). They keep the raw `claude` output collapsed by default in the run UI; the maintainer expands the group only when investigating a failure. The job summary line gets the human-readable diagnostic regardless.
- **The job summary** (`$GITHUB_STEP_SUMMARY`) is the FR-6 actionable-diagnostic surface. It names the mechanism, the offending artifact, the rule, the disconnected servers (with name+status), and the remedial hint — the four FR-6-required fields.

### SHA-pinning of third-party actions

KB-github-actions-platform non-negotiable #1: pin any non-`actions/*` and non-`github/*` action to a 40-character commit SHA. Two third-party actions are referenced above; both must be SHA-pinned at implementation time. The version comment next to each SHA documents the human-readable tag for future readers.

| `uses:` reference | SHA pin (to be filled at implementation) | Version comment | Source-of-truth lookup |
|---|---|---|---|
| `actions/checkout` | first-party `actions/*` — major-version tag is acceptable, but SHA is safer | `# v4.x.y` | `https://github.com/actions/checkout/releases` |
| `devcontainers/ci` | third-party — **must** be SHA-pinned | `# v0.3.x` | `https://github.com/devcontainers/ci/releases` |

The author of the workflow at execution time resolves both SHAs from the release pages above, pastes the 40-character SHA, and appends the `# vX.Y.Z` comment. This document does not pre-fill the SHA values because they can move between this design's date and the implementation date; the operator at implementation time should look up the current release.

**Plan task contract for SHA resolution.** To prevent the workflow regressing to tag-pinning when the plan-author wires up the implementation, the Plan must include a dedicated task with the following contract: *"For each third-party action in the SHA-pinning table, resolve a 40-character commit SHA pinned to a specific released tag (not a branch or floating ref). The resolution procedure is: (1) visit the release page named in the table; (2) select the latest non-prerelease tag at or below the Claude Code version pinned in the devcontainer's `claude-code` Feature (so the action's release date is no newer than the SDK whose `system/init` shape we depend on); (3) click into the tag, copy the 40-character SHA from the commit ref; (4) paste in the `uses:` line and add `# vX.Y.Z` as a same-line comment naming the released tag. Do not substitute a tag-name (`@v4`) for a SHA. Do not substitute a branch-name (`@main`) for a SHA. Per-task execution result records the resolved SHA and the tag it was sourced from."* This contract is explicit so an automated executor cannot silently downgrade to tag-pinning to "make it work."

The `devcontainers/ci` action is published by the `devcontainers` GitHub org (which is operated by the same Microsoft team that owns the devcontainer spec — see `https://github.com/devcontainers`). It is not strictly first-party to GitHub or Anthropic, so the SHA-pinning rule applies. If a future feature wants to swap in a different mechanism (e.g., direct `docker buildx build` of the devcontainer image and `docker run` of the smoke), that's a legitimate alternative; this design picks the canonical Microsoft-published action for now.

### Caching and artifacts

None. The smoke is a single-invocation health check; there is nothing to cache between runs (the devcontainer image cache is owned by the runner's Docker layer cache, not by the workflow), and there are no artifacts to emit (the diagnostic surfaces in the job summary, which is the workflow's natural log surface).

If the workflow's runtime exceeds NFR-4 because devcontainer rebuilds dominate, the canonical mitigation is a Codespaces-side prebuild (Q-CICD-2) — not a workflow-side cache, which would not survive runner-to-runner.

### Secrets, environments, OIDC

None of the above. The workflow:

- Reads no secrets. The smoke uses the devcontainer image's filesystem and the `claude` CLI; the existing devcontainer-provisioned credentials (per `containerEnv` injection from Codespaces secrets) are NOT present in CI because CI is not a Codespace. The `claude` CLI runs against whatever credentials are baked into the image at build time, which for CI is the unauthenticated state — and that is the correct posture, because the smoke is asking "does each MCP server *initialize* in the connected state," not "can the model successfully complete a task." MCP server initialization happens before any model-side auth is needed, so the SDK's `system/init` event is emitted regardless of credential state for the actual model invocation.
- Has no `environment:` declaration. This is not a deploy.
- Does not federate to any cloud (no OIDC).

This is the right posture per NFR-7 (no new credential surface). Future hardening could add a model API key to allow the noop prompt to complete cleanly, but the current smoke does not require it — the workflow captures the `system/init` event before the prompt is dispatched to the model, so the model-side auth state is irrelevant. If a future Claude Code version requires authentication for `--bare -p noop` to even produce the `system/init` event, that would be a CI-fragility concern flagged at Q-CICD-1 (Claude Code version drift).

### FR-5 sibling-awareness note

In v0.3.0 the layer's scope expanded to a second workflow at `.github/workflows/gitnexus-grammar-skip-calibration.yml` (FR-4c, specified below). The FR-5 design above is unchanged — its triggers, runner choice, permissions, diagnostic shape, and SHA-pinning posture all carry forward as-is. What changes is the layer-level framing: the `.github/workflows/` directory now holds two files rather than one, and the SHA-pinning Plan-task contract, the actionlint Plan-task contract, and the convention-establishment paragraph all apply symmetrically across both. Cross-references in the FR-5 section to "the workflow" should be read as "the FR-5 workflow"; cross-references to "this workflow file" remain unambiguous within their local subsection.

## FR-4c — Calibration CI wiring

The Codespaces designer's split of FR-4 into three sub-mechanisms creates a new CI/CD obligation. FR-4a is a sub-100-ms static check inside `postCreate.sh` (no CI involvement). FR-4b is a separate opt-in scratch-install behavioral-calibration script at `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` that performs the actual upstream-behavioral check (scratch-dir install, Signal 1 stderr regex, Signal 3 artifact absence) and emits one event per run to `.claude/runtime/mcp-events.jsonl` per ADR-0037. FR-4b is maintainer-only and does not run on every devcontainer rebuild. **FR-4c is the CI wiring that makes the FR-4b script actually run on a schedule and on every relevant change.** The trap to avoid, explicitly named by the user during the FR-4 reshape: "If it ends up as a maintainer-only shell script that nobody invokes for six months, option 3 degrades silently." This section's design is the structural defence against that trap.

### Why a CI surface for FR-4b at all

FR-4b on its own is a maintainer ergonomics improvement — a sharper, longer-running version of the FR-4a static check that catches upstream drift the static check cannot see. Without scheduled invocation, it answers a question that nobody asks; the value of the behavioral check decays to zero between manual runs. CI is the natural place to ask the question regularly. Three triggers cover the three drift modes:

- **Gradual upstream drift.** GitNexus changes its native-binary install behavior between the tag pinned in `versions.env` and the next pin bump. A weekly cron catches this at the cost of one workflow run per week — independent of whether the project is actively merging PRs.
- **Pin-bump drift.** A maintainer bumps the GitNexus tag in `versions.env` but does not realize the new tag changed install behavior (e.g., the grammar-skip warning text changed from "Skipping" to "Omitting" — a real failure mode the FR-4b script is designed to surface). An on-change trigger on `versions.env` catches this at the moment of the bump rather than waiting for the next cron tick.
- **Maintainer-initiated manual check.** `workflow_dispatch` lets the maintainer re-run the calibration at will (e.g., after investigating an upstream issue, before opening a PR that bumps the pin, after a Codespaces image rebuild).

### File location and identifier

- **Path:** `.github/workflows/gitnexus-grammar-skip-calibration.yml`
- **Display name** (the `name:` key in the workflow YAML): `GitNexus Grammar-Skip Calibration`
- **Job identifier** (key under `jobs:`): `calibrate`

File naming follows the convention established by FR-5 (`<purpose>-<verb>.yml`, lowercase, hyphen-separated). The display name is Title Case, descriptive.

### Trigger configuration

```yaml
on:
  schedule:
    - cron: '0 7 * * 1'
  pull_request:
    paths:
      - '.devcontainer/versions.env'
      - '.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh'
  workflow_dispatch: {}
```

Rationale for each trigger:

- **Weekly cron — `'0 7 * * 1'` (Monday 07:00 UTC).** The cron expression picks a quiet maintainer window: Monday morning UTC corresponds to Sunday late-night / Monday early-morning across most contributor timezones, so a failed calibration surfaces at the start of the maintainer's working week rather than across a weekend. The day-of-week choice (Monday rather than Friday) means a failing calibration is investigated in fresh maintainer time, not at the end of a working week when fixes might wait two days. Weekly cadence is conservative: upstream GitNexus releases are sporadic, and a daily cron would burn ~6 redundant runs per week. A future tightening to twice-weekly is a low-cost adjustment if drift is observed mid-week; flagged loosely as part of the maintainer's regular review of the calibration's value.

  Why not align with FR-5's empty cron: FR-5 has none. The FR-4c cron exists precisely because the question it asks (has upstream changed?) cannot be answered from PR diffs alone, so it must run independently of PR activity.

- **`pull_request` with `paths: ['.devcontainer/versions.env', '.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh']`.** The pin-bump trigger. Any PR that touches `versions.env` runs the calibration against the new pin before merge. Any PR that touches the calibration script itself runs it before merge so the script's authoring doesn't silently regress. Narrowed to two exact paths rather than `.devcontainer/**` because the FR-5 smoke already covers the broader `.devcontainer/**` surface for connectivity questions; the calibration is asking a narrower question (does the GitNexus grammar-skip mechanism work?) for which only those two files matter. Running on every `.devcontainer/**` change would create CI cost without proportional signal.

  The `pull_request` event (not `pull_request_target`) is correct for the same reasons FR-5 uses it: no elevated tokens needed, no secrets accessed, attacker blast-radius is the runner only.

- **`workflow_dispatch: {}`.** Manual re-run. Empty `{}` because no inputs are needed; the calibration is parameterless.

### Permissions

```yaml
permissions:
  contents: read
```

Identical posture to FR-5. The calibration reads the PR / branch tree (`versions.env`, the calibration script, the devcontainer config to build the image), runs the script inside the built devcontainer, and surfaces results via `$GITHUB_STEP_SUMMARY` and (for the maintainer to view) the workflow's pass/fail status. It does not write back to the repo, does not comment on PRs, does not deploy, does not federate to any cloud. Workflow-level declaration (one job, one scope).

### Concurrency

```yaml
concurrency:
  group: gitnexus-calibration
  cancel-in-progress: false
```

**Recommendation: set a concurrency group, but do NOT cancel in-progress runs.** Rationale:

- The three triggers can fire concurrently. A `versions.env` PR opened on Monday at 07:00 UTC would race the cron. A maintainer firing `workflow_dispatch` while the cron is mid-run is plausible. Without a concurrency group, both runs proceed in parallel, both perform the (identical) scratch-install behavioral check, both emit a `mcp-events.jsonl` event, and both produce a `$GITHUB_STEP_SUMMARY`. The duplicate event is the actual problem: ADR-0037's mcp-events surface is meant to record discrete invocations, and two near-simultaneous emissions for "the same calibration" create downstream confusion (e.g., for the Q-CICD-10 stale-calibration banner, which counts time since the last event).
- Setting the group at `gitnexus-calibration` (a constant, not a branch- or PR-scoped expression) means **at most one calibration runs at a time across the whole repo**. Queued runs wait, then proceed; they do not get cancelled. `cancel-in-progress: false` is the load-bearing flag here — cancelling would lose the just-finished scratch-install work and degrade the signal.
- The cost of queuing is bounded: each run is well under 2 min (see NFR-4 commitment below), so a queue depth of two means roughly 4 minutes worst-case end-to-end. Acceptable.

Why not skip concurrency entirely (as FR-5 does): FR-5 has no event-surface emission and no shared-state mutation, so parallel runs are genuinely independent. FR-4c writes to `mcp-events.jsonl` and the duplicate-write is the harm; concurrency control eliminates it.

### Job and step shape

```yaml
jobs:
  calibrate:
    name: GitNexus grammar-skip calibration (devcontainer-image fidelity)
    runs-on: ubuntu-latest
    timeout-minutes: 5

    steps:
      - name: Checkout
        uses: actions/checkout@<SHA>  # v4.x — see SHA-pinning table below

      - name: Build and run devcontainer
        uses: devcontainers/ci@<SHA>  # v0.3.x — see SHA-pinning table below
        with:
          runCmd: |
            set -euo pipefail

            echo "::group::FR-4b calibration — GitNexus grammar-skip behavioral check"

            # The script is owned by the Codespaces layer; CI just invokes it.
            # Exit 0 = pass (no behavioral drift).
            # Exit non-zero = drift detected (the script's responsibility to set
            # the exit code based on Signal 1 / Signal 3 evaluation).
            # The script emits its own event to .claude/runtime/mcp-events.jsonl
            # per ADR-0037 — CI does NOT duplicate that emission.

            CALIBRATE_OUTPUT="$(mktemp)"
            trap 'rm -f "$CALIBRATE_OUTPUT"' EXIT

            if .devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh \
                 > "$CALIBRATE_OUTPUT" 2>&1; then
              CALIBRATE_RC=0
            else
              CALIBRATE_RC=$?
            fi

            echo "::endgroup::"

            # Always surface the script's stdout/stderr in the run log for
            # post-hoc investigation, whether the run passed or failed.
            echo "--- calibration script output (rc=$CALIBRATE_RC) ---"
            cat "$CALIBRATE_OUTPUT"
            echo "--- end calibration script output ---"

            if [ "$CALIBRATE_RC" -eq 0 ]; then
              {
                echo "## GitNexus Grammar-Skip Calibration — PASS"
                echo ""
                echo "**Mechanism:** FR-4c calibration CI wiring (workflow \`gitnexus-grammar-skip-calibration.yml\`)."
                echo "**Calibration script:** \`.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh\` (FR-4b, owned by Codespaces layer)."
                echo "**Result:** Signal-1 stderr regex matched as expected; Signal-3 artifact absence confirmed; the pinned GitNexus tag in \`.devcontainer/versions.env\` continues to honor the grammar-skip contract."
                echo "**Event emission:** the script wrote a \`calibration_result\` event to \`.claude/runtime/mcp-events.jsonl\` per ADR-0037 (see Q-CICD-11 re: schema-extension status)."
              } >> "$GITHUB_STEP_SUMMARY"
              exit 0
            fi

            # FR-6 actionable diagnostic — drift detected.
            {
              echo "## GitNexus Grammar-Skip Calibration — FAIL"
              echo ""
              echo "**Mechanism:** FR-4c calibration CI wiring (workflow \`gitnexus-grammar-skip-calibration.yml\`)."
              echo "**Calibration script:** \`.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh\` (FR-4b, owned by Codespaces layer)."
              echo "**Offending grammar:** see script output above — the script names which grammar (Dart or Proto) failed which Signal-N check."
              echo "**Rule violated:** the pinned GitNexus tag in \`.devcontainer/versions.env\` no longer honors the grammar-skip contract that ADR-0007 / the FR-4 design depends on."
              echo "**Exit code:** \`$CALIBRATE_RC\` (non-zero = behavioral drift; see script source for exit-code semantics)."
              echo ""
              echo "**Remedial hint:** investigate the upstream GitNexus tag change since the \`versions.env\` pin was last bumped. The likely root causes are (a) upstream changed its grammar-skip warning text (Signal 1 regex drift) or (b) upstream changed how it surfaces skipped-grammar artifacts (Signal 3 path drift). Mitigations: pin to the prior GitNexus tag in \`versions.env\` until upstream is investigated; or amend the FR-4b script to recognize the new signal shape (and bump its contract version); or, if the upstream behavior is genuinely incompatible, open a follow-on feature to revise the grammar-skip mechanism."
              echo ""
              echo "**Trigger that fired this run:** \`${{ github.event_name }}\` (one of: \`schedule\` weekly cron, \`pull_request\` on \`versions.env\` / script change, \`workflow_dispatch\` manual re-run)."
            } >> "$GITHUB_STEP_SUMMARY"

            exit 1
```

Notes on the step shape:

- **`timeout-minutes: 5`** is tighter than FR-5's `timeout-minutes: 8`. The calibration's expected p95 is well under 2 min (see NFR-4 commitment below); 5 minutes gives 2.5x headroom while staying within NFR-4's overall budget for the layer. If the calibration ever exceeds 5 minutes the runaway is almost certainly an upstream-install hang (npm fetching a broken tarball, GitNexus's native-binary install spinning), and a hard timeout is the right outcome — fail loud and surface in the next maintainer touch.
- **`set -euo pipefail`** in the shell block — same posture as FR-5 and as the project's existing `.devcontainer/postCreate.sh`.
- **The script's exit code is the contract.** CI does not re-implement the Signal 1 / Signal 3 logic; that is the script's responsibility (FR-4b, Codespaces layer). CI's contract is: invoke the script; capture stdout+stderr; surface them; honor the exit code. This keeps the behavioral check authoritatively in one place. If a future revision splits the script across multiple exit codes (0 = pass, 1 = drift, 2 = environment error), the FR-6 diagnostic above can be extended to distinguish them; the current design treats any non-zero as "drift detected" and lets the script's stdout carry the discrimination.
- **The script — not the workflow — writes the `mcp-events.jsonl` event.** This is explicit because there are two reasonable shapes here and the wrong one introduces a dual-emission bug. The script is the authoritative emitter (it knows what happened; CI is downstream of it). CI confirms the file was touched only as part of the Q-CICD-10 stale-banner concern; it does not write to the file.
- **No `\${{ github.event.* }}` interpolation into the `run:` block** except for `${{ github.event_name }}`, which is a controlled enum (one of `schedule`, `pull_request`, `workflow_dispatch`) populated by GitHub itself — not by PR-author input. This is safe per KB-github-actions-platform non-negotiable #3 (script injection); the interpolation is into a Markdown summary, not a shell-interpreted position, and the value is GitHub-controlled.
- **`::group::` / `::endgroup::`** is used to collapse the calibration's verbose scratch-install output by default, matching FR-5's posture for the `claude --bare` output.

### SHA-pinning of third-party actions

The same plan-author task contract from FR-5 applies. The FR-4c workflow uses the same two third-party actions as FR-5 (`actions/checkout` first-party, `devcontainers/ci` third-party); both must be SHA-pinned at implementation time. The Plan-task contract is the same as FR-5's — see "Plan task contract for SHA resolution" in the FR-5 section above. The same SHAs the plan-author resolves for FR-5 should be reused for FR-4c (one resolution effort, two `uses:` lines), so the two workflows pin the same version. If a future feature wants the two workflows to pin different versions of `devcontainers/ci` (e.g., for a phased upgrade), that's a deliberate departure noted at the time.

The calibration script itself (`.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh`) is in-repo and therefore does not need pinning — it is checked out as part of the PR / branch tree.

### Diagnostic shape and FR-6 alignment

The FR-6 dual-stream convention established by FR-5 (write to `$GITHUB_STEP_SUMMARY` for the maintainer to see in the GitHub run UI; let upstream events handle the event-surface) is honored here, with one structural difference:

- FR-5 emits no `mcp-events.jsonl` event from the workflow; the events surface is updated separately by `postCreate.sh` etc.
- FR-4c also emits no `mcp-events.jsonl` event from the workflow — but the **script the workflow invokes** does. That delegation keeps the event surface authoritatively owned by the Codespaces layer (the script). CI's contribution to the diagnostic story is the `$GITHUB_STEP_SUMMARY` block, which names the mechanism (FR-4c), the calibration script path, the offending grammar (surfaced from the script's stdout), the Signal-N that failed, and the remedial hint.

The four FR-6-required fields appear in the FAIL summary above:

1. **Mechanism:** "FR-4c calibration CI wiring".
2. **Offending artifact / grammar:** named in the script output (re-surfaced by CI in the log block above the summary).
3. **Rule violated:** "the pinned GitNexus tag … no longer honors the grammar-skip contract."
4. **Remedial hint:** the multi-option block (pin back, amend script, open follow-on).

### Trap-avoidance observability

The user explicitly named the trap to avoid: an FR-4b script that "ends up as a maintainer-only shell script that nobody invokes for six months" degrades the feature silently. The defences in this design:

- **The CI workflow itself is the primary observability surface.** Weekly cron means there is a forced invocation cadence the maintainer cannot accidentally skip. A failing cron run surfaces in GitHub's Actions tab and (for maintainers who watch the repo) in failed-workflow notifications.
- **The `mcp-events.jsonl` event surface.** The script emits a `calibration_result` event per ADR-0037; downstream tooling that audits the events surface (e.g., the `auditing-mcp` skill, or a future Codespaces-side stale-banner) can read the event timestamp to determine whether calibration is current.
- **Stale-calibration banner — Codespaces concern.** A useful additional defence is a banner emitted by `postCreate.sh` if the most recent `calibration_result` event is more than N weeks old (N being a Codespaces design call; the natural value is 4 weeks, giving a week's grace beyond a missed weekly cron). This belongs in the Codespaces layer (postCreate is theirs); surfaced as **Q-CICD-10** so the composer can route the question to design-codespaces.
- **Plan-task contract for the calibration script's CI-discoverable shape.** The Plan must include a task verifying that the FR-4b calibration script (a) exits non-zero on drift, (b) writes its `mcp-events.jsonl` event before exiting, and (c) names the offending grammar in its stdout in a way the FR-4c workflow's `$GITHUB_STEP_SUMMARY` can surface. These are Codespaces-layer responsibilities, but the FR-4c CI design depends on them, so they enter the cross-layer contract.

### NFR alignment

- **NFR-4 (5-minute budget).** The FR-4c calibration's CI runtime decomposes as: runner provisioning (~30 s), devcontainer image build (estimated 2 min from a cold cache; ≪1 min if a prebuild lands — Q-CICD-2 applies symmetrically here), calibration script run (~30 s: scratch-dir `npm install` of GitNexus, stderr capture, filesystem check), summary emission (negligible). **Commitment: under 2 min p95**, well under NFR-4's 5-minute ceiling. The image-build time dominates and is shared with FR-5; a Codespaces-side prebuild benefits both workflows.
- **NFR-7 (no new credentials).** The calibration runs against the public `gitnexus` npm package; no auth needed; no secrets read; no `ANTHROPIC_API_KEY` involved. The unauthenticated-CLI posture from FR-5 carries over. NFR-7 preserved.
- **NFR-13 (MCP event surface — ADR-0037 schema).** The FR-4b script writes a `calibration_result` event type to `mcp-events.jsonl`. ADR-0037's canonical event types may not yet name `calibration_result`. If the schema does not currently allow the type, an additive extension is needed (the existing enum gains one value; existing consumers ignore unknown types per ADR-0037's forward-compatibility posture, but the schema should be updated). This is a cross-layer Codespaces+CI/CD concern — the event is emitted by Codespaces but motivated by CI/CD's invocation cadence. Surfaced as **Q-CICD-11** for the composer.

### Convention extended by FR-4c

The two-workflow shape extends the convention this layer establishes:

- A workflow file may run on `schedule:`; the Monday 07:00 UTC slot is the first cron cadence in the repo's CI.
- `concurrency:` with `cancel-in-progress: false` is the right shape when a workflow has side effects (event-surface writes) but no exclusive-lock requirement. Future workflows with similar side effects should follow this pattern.
- A workflow may invoke an in-repo script and treat the script's exit code as its contract, with no replication of the script's logic at the workflow level. This keeps domain logic in one place.
- `timeout-minutes:` is tightened from FR-5's 8 down to 5 for the calibration; the convention is "set the timeout against the actual expected p95 + a defensible multiplier", not a flat workflow-level default.

## Workflow Inventory (per Blueprint template)

| Workflow File | Triggers | Purpose | Concurrency Group |
|---|---|---|---|
| `.github/workflows/mcp-connectivity-smoke.yml` | `pull_request` (paths-filtered) + `workflow_dispatch` | FR-5: assert every server in `.mcp.json` reports `status: connected` from the Agent SDK `system/init` event after a fresh devcontainer provision. Fail any PR that breaks the invariant. | None (not a deploy; parallel runs are safe). |
| `.github/workflows/gitnexus-grammar-skip-calibration.yml` | `schedule:` (weekly `0 7 * * 1`) + `pull_request` on `versions.env` / calibration script + `workflow_dispatch` | FR-4c: invoke the Codespaces-owned FR-4b calibration script on a regular cadence and on every pin bump, so the behavioral grammar-skip contract does not silently degrade between manual maintainer invocations. Fail when the script reports drift. | `gitnexus-calibration` (constant group, `cancel-in-progress: false`) — prevents duplicate `mcp-events.jsonl` emissions from racing triggers. |

## Job Graph

**FR-5 (`mcp-connectivity-smoke.yml` / `smoke`):**

```
checkout ──► devcontainers/ci (build image, run smoke)
                    │
                    └─► claude --bare -p noop --output-format stream-json
                                │
                                └─► jq filter on system/init.mcp_servers[] for status != "connected"
                                            │
                                            ├─► empty result: PASS (exit 0, job summary "all connected")
                                            └─► non-empty:   FAIL (exit 1, job summary names servers + FR-6 hint)
```

**FR-4c (`gitnexus-grammar-skip-calibration.yml` / `calibrate`):**

```
checkout ──► devcontainers/ci (build image, run calibration)
                    │
                    └─► .devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh
                                │
                                ├─► (side effect) write `calibration_result` event to .claude/runtime/mcp-events.jsonl
                                │
                                └─► exit code
                                            │
                                            ├─► 0:        PASS (job summary "calibration honored")
                                            └─► non-zero: FAIL (job summary names grammar + Signal-N + FR-6 hint)
```

Each workflow has one job, one runner. No matrix (the devcontainer is the single execution environment; running calibration across multiple GitNexus versions would be a different feature, and the FR-4c calibration's whole purpose is to validate exactly the one tag pinned in `versions.env`). No fan-out / fan-in. The two workflows are independent — they do not depend on each other's job status, share no concurrency group, and consume / produce no common artifacts. The shared dependency is the devcontainer image build itself, which Docker layer-caches per-runner.

## Reusable Actions / Composite Actions

None introduced. The workflow uses two third-party actions (`actions/checkout`, `devcontainers/ci`) as-published; no project-side composite action or reusable workflow is created.

Rationale: KB-github-actions-design's pattern catalogue says to extract a reusable workflow or composite action when duplication appears across workflows. This is the project's first workflow; there is no duplication to extract from. If a follow-on feature adds a second workflow that also wants "build the devcontainer and run a command inside it" (plausible — Q-CICD-3 about a merge-time smoke would be one such), that would be the moment to extract `.github/actions/devcontainer-runner/action.yml` or a reusable `.github/workflows/devcontainer-smoke.yml`. Not now.

## Secrets, Variables & Environments

| Name | Scope | Type | Source | Used By |
|---|---|---|---|---|
| (none) | — | — | — | — |

No secrets read, no environments declared, no repo-variables or org-variables consumed. The workflow operates entirely on the PR's checked-out tree and the devcontainer image built from it.

## Permissions

| Workflow / Job | `permissions:` block | Justification |
|---|---|---|
| `mcp-connectivity-smoke.yml` / `smoke` | `contents: read` | Reads the PR's tree (`.mcp.json`, `.devcontainer/**`) and runs commands inside the built image. Does not write back to the repo, does not comment on PRs, does not deploy, does not use OIDC. The default `GITHUB_TOKEN` would inherit broader scopes depending on repo defaults; the explicit declaration locks scope to read-only. |
| `gitnexus-grammar-skip-calibration.yml` / `calibrate` | `contents: read` | Reads the branch tree (`.devcontainer/versions.env`, the calibration script, the devcontainer config) and runs the calibration inside the built image. No PR comments (the workflow's pass/fail status is the surface), no deploy, no OIDC. Same posture as FR-5. |

## Caching & Artifacts

| Cache / Artifact | Key | Scope | Retention |
|---|---|---|---|
| (none) | — | — | — |

The devcontainer image's Docker-layer cache lives in the runner's local filesystem and is managed by Docker/BuildKit, not by the workflow. If Q-CICD-2 (prebuild for CI runtime budget) is acted on, the prebuild lives on the Codespaces side, not as a GitHub Actions `actions/cache` entry — because the devcontainer image cache survives across `docker build` invocations of the same Dockerfile but not naturally across GitHub-hosted runner instances. Cross-runner caching of a built devcontainer would require an additional step (push the built image to a registry such as GHCR, pull on subsequent runs), which is more machinery than the carve-out justifies.

## Environments & Promotion

| Environment | Protection Rules | Required Reviewers | Wait Timer | Deployment Branches |
|---|---|---|---|---|
| (none — this is not a deploy) | — | — | — | — |

## Failure & Rollback

- **Failed-deploy behavior:** N/A — not a deploy.
- **Rollback workflow:** N/A — not a deploy. The PR check failure itself prevents merge; rolling back is "fix the broken `.mcp.json` or devcontainer change in the PR."
- **Notification routing:** GitHub's built-in PR-check status. The maintainer sees the failing check in the PR UI and the failing job in the workflow run page. No Slack / email integration in scope (Q-CICD-6 if the maintainer ever wants it).

## Lint findings

The `mcp__actionlint-mcp` MCP tools were unavailable for this run (the deferred-tool-schema issue that triggered this fallback). The `actionlint` binary is not on the runtime PATH in this main-agent environment either, so a binary-level lint pass was not run. **Both** workflows' YAML has been hand-checked against the KB-github-actions-platform review checklist (`KB-github-actions-platform/SKILL.md` "Review checklist" section + `references/security.md` non-negotiables); the table below applies to each workflow:

| Check (from KB review checklist) | Status |
|---|---|
| Third-party actions SHA-pinned with version comments | **Specified as required at implementation** — the SHA values are intentionally not pre-filled in this document because the operator at implementation time should look up the current release SHA. The SHA-pinning table above names both actions, the version comment format, and the source-of-truth release-page URL. |
| Explicit `permissions:` block, minimal | **PASS** — `contents: read` only. |
| No `${{ github.event.* }}` or `${{ github.head_ref }}` interpolated into `run:` blocks | **PASS** — the `runCmd:` value is a static heredoc. No PR-author-controlled string crosses into shell. |
| `pull_request_target` used? | **NOT USED** — `pull_request` is used (the safer choice for a check that does not need elevated tokens). |
| Deprecated patterns (`set-output`, `save-state`, Node 12/16 actions) | **PASS** — no `set-output` or `save-state`. The two actions referenced (`actions/checkout` v4+, `devcontainers/ci` v0.3+) are current. |
| Deploy workflow wrapped in `concurrency:` + `environment:` | **N/A** — not a deploy. Concurrency intentionally omitted. |
| Cache keys correct | **N/A** — no cache. |
| Secrets passed only to jobs that need them | **N/A** — no secrets. |
| Matrix combinations meaningful | **N/A** — no matrix. |
| `timeout-minutes:` set on long jobs | **PASS** — `timeout-minutes: 8`. |
| Logs free of secret leakage (no `echo "$SECRET"`) | **PASS** — no secret reads anywhere; the only `printf`/`echo` writes go to `$GITHUB_STEP_SUMMARY` (the FR-6 diagnostic) and stdout (the `claude` output, which is the smoke's purpose). |

Recommendation for implementation: the operator authoring the workflow file from this design should run `actionlint` (the binary, install via `brew install actionlint` or `go install github.com/rhysd/actionlint/cmd/actionlint@latest`) against the file before committing. If `actionlint-mcp` is restored in a subsequent session, `mcp__actionlint-mcp__lint_workflow` is the equivalent. The hand-check above gives confidence the workflow is structurally sound; a binary lint pass is the belt-and-braces.

**Plan task — actionlint deferral (both workflows).** The Plan must include a task with the following contract: *"Before committing either `.github/workflows/mcp-connectivity-smoke.yml` or `.github/workflows/gitnexus-grammar-skip-calibration.yml`, run `actionlint <file>` (or `mcp__actionlint-mcp__lint_workflow` if the actionlint MCP server is restored to the project's `.mcp.json` between this design's date and the implementation date) against each file. Record the lint output verbatim in the per-task execution result. If lint reports any error in either file, fix and re-run before commit; if lint reports only warnings, record them in the execution result with a justification for proceeding. Both files must pass before either is committed — a half-committed `.github/workflows/` directory is not a valid intermediate state."* This makes the lint pass a recorded artifact rather than an unverified claim and ensures the two-workflow shape lands atomically.

## Convention this layer establishes

Because `.github/workflows/` is greenfield in this project, these two workflows' shape becomes the convention until a future feature deliberately revises it. The two-workflow shape (FR-5 PR-smoke + FR-4c scheduled calibration) is itself part of the convention: the directory holds **two** files at the end of this feature, not one, and future workflows enter alongside them rather than displacing them. The conventions established by this design:

- **Workflow file naming:** `<purpose>-<verb>.yml` (e.g., `mcp-connectivity-smoke.yml`, `gitnexus-grammar-skip-calibration.yml`). Lowercase, hyphen-separated.
- **Workflow `name:` field:** Title Case, descriptive. ("MCP Connectivity Smoke"; "GitNexus Grammar-Skip Calibration".)
- **Job-id naming:** short, single-word where possible (`smoke`, `calibrate`).
- **SHA-pinning:** all third-party actions pinned to 40-character SHAs; first-party `actions/*` may use major-version tags (the `actions/checkout` exception in the table); both get a `# v<X.Y.Z>` comment. When the same action appears in multiple workflows in the same release, the same SHA is used in both — one resolution effort, repeated `uses:` lines.
- **Permissions:** explicit block on every workflow, starting from `contents: read` and adding only what each job needs.
- **Timeouts:** every job declares `timeout-minutes:` against its expected runtime + headroom. The timeout is right-sized per workflow, not a project-wide flat default.
- **Diagnostics:** failure modes write a structured Markdown summary to `$GITHUB_STEP_SUMMARY` honoring FR-6's four required fields (mechanism, artifact, rule, remedial hint) whenever the workflow is implementing a project-named mechanism. Where a workflow delegates work to an in-repo script that emits its own `mcp-events.jsonl` event, the workflow does not duplicate the event emission (the script is authoritative).
- **Triggers:** path-filtered `pull_request:` for PR-time checks; `schedule:` for cadence-driven checks (Monday 07:00 UTC is the first established cron slot); `workflow_dispatch:` added on every workflow for manual re-runs.
- **Concurrency:** set when the workflow has side effects (event-surface writes, shared-state mutation) using a constant group with `cancel-in-progress: false`. Skip when the workflow is side-effect-free.
- **No secrets / no OIDC / no environments** unless the workflow demonstrably requires them.

Future workflows in this project should follow these conventions or deliberately depart from them with rationale. A future feature that introduces a deploy workflow will necessarily depart on permissions, concurrency, environments, and OIDC — that's expected; the convention here is for CI checks, not deploys.

## Architectural Questions for Composer

These are surfaced for the cross-layer composer (and ultimately the maintainer) to resolve before Plan Authoring. None of these is a blocker for this layer's design; each is an explicit hand-off.

- **Q-CICD-1 (Claude Code version pinning in CI).** The smoke depends on the Agent SDK `system/init` event surface. T-002 Finding 7 notes that specific MCP behaviors pin to specific Claude Code CLI versions. The smoke inherits whatever Claude Code version the devcontainer's `claude-code` Feature installs; that's a Codespaces-layer pin, not a CI/CD-layer pin. If a future change sets the devcontainer Feature's `version: latest`, every CI run becomes vulnerable to upstream-released breakage. **Recommendation:** the devcontainer Feature should pin to an exact Claude Code version. **Owner:** design-codespaces (decides the pin); design-composer reconciles if a cross-layer disagreement appears.

- **Q-CICD-2 (CI runtime budget mitigation if NFR-4 is breached).** The estimated p95 of under 4 minutes assumes a typical devcontainer image-build of 2-3 minutes. If real-world runs exceed NFR-4's 5-minute ceiling, the canonical mitigation is a Codespaces-side prebuild (publish the devcontainer image to GHCR; pull on each workflow run instead of rebuilding). That prebuild surface lives in the Codespaces layer, not CI/CD. **Recommendation:** measure first; if budget is exceeded, the maintainer requests a follow-on feature to add the prebuild. **Owner:** design-codespaces (if invoked); maintainer (decides whether to invoke).

- **Q-CICD-3 (merge-time smoke).** The current workflow is PR-gated only. A push-to-main equivalent that catches merge-races, branch-fast-forward losses, or upstream MCP regressions discovered after PR review would be a natural extension. **Recommendation:** out of scope for this carve-out (PRD's FR-5 specifies PR-time only). If adopted later, the extracted reusable workflow / composite action would emerge then. **Owner:** maintainer (decides whether to invoke a follow-on feature).

- **Q-CICD-4 (nightly upstream-health smoke).** A `schedule:` trigger that runs the smoke nightly would catch silent upstream MCP server outages or package-registry breakages that nobody notices because no PR is open. **Recommendation:** out of scope for this carve-out. If adopted later, would share the workflow body with the PR-gated form. **Owner:** maintainer.

- **Q-CICD-5 (PR concurrency / cancel-in-progress).** Not set in the current design (default run-to-completion is fine for a check with no side effects). If maintainer ergonomics prefers cancelling stale in-flight runs when a PR is force-pushed, adding `concurrency: { group: smoke-${{ github.head_ref }}, cancel-in-progress: true }` is the right shape. **Recommendation:** add when maintainer reports ergonomics friction, not before. **Owner:** maintainer.

- **Q-CICD-6 (notification routing).** GitHub's built-in PR check status is the only notification channel in scope. If the maintainer ever wants Slack / email on failure, the canonical pattern is `if: failure()` with a notification action — but that adds a third-party action surface and a secret (webhook URL). **Recommendation:** keep the workflow minimal until a need is demonstrated. **Owner:** maintainer.

- **Q-CICD-7 (cross-layer interaction with FR-3 audit rule).** FR-3's `auditing-mcp` parity rule (`audit_op11_*.py`) also reads `.mcp.json` and ADR-0041; the smoke does not invoke it. There is an option to chain the smoke and the parity audit (run both in the same workflow, fail if either fails). **Recommendation:** keep them separate. The parity rule is a static-analysis check that runs in the audit gate at Gate-6 (per ADR-0043); the smoke is a runtime connectivity check. Running them together would conflate two failure modes and inherit the slower one's budget. The two are complementary, not duplicative. **Owner:** design-composer reconciles if both layers' designers disagree; this design recommends keeping them separate.

- **Q-CICD-8 (devcontainer image and Claude Code authentication in CI — upgraded to Plan task).** The smoke captures `system/init` before any model-side auth is required. T-002's note carries this with a caveat; per I-DR-003, this assumption is **verified pre-merge** rather than monitored post-merge. The Plan must include the validation task described in the D-0007 "Pre-merge validation of the unauthenticated-CLI assumption" paragraph above: run `claude --bare -p "noop" --output-format stream-json` in the project's devcontainer in the unauthenticated state CI will use, and confirm `system/init` is emitted with a populated `mcp_servers[]`. If validation fails, the fallback is a read-only `ANTHROPIC_API_KEY` repo secret scoped to this workflow + an explicit, documented NFR-7 deviation in the Blueprint. **Owner:** Plan author (adds the task); maintainer (executes the validation before merge); design-composer (records the NFR-7 deviation if the fallback path is taken).

- **Q-CICD-9 (AC-FR-5-a/b/c PRD-literal reconciliation).** The PRD's AC-FR-5-a/b/c literally name `claude mcp list`; this design substitutes `claude --bare -p "noop" --output-format stream-json | jq` per the synthesis decision D-0007 (see the "PRD-literal reconciliation for AC-FR-5-a/b/c" paragraph in §D-0007 above). The substitution preserves the behavioral intent but the AC text and the implementation diverge. The composer should resolve this by either (a) rewriting AC-FR-5-a/b/c in the Blueprint to reference the substitute invocation (recommended; the substitute is the contract-bearing path), or (b) leaving the AC literal as `claude mcp list` and requiring the implementation to wrap or shadow that command — which would re-introduce the very contract-uncertainty the substitution is designed to escape, and is **not** recommended. PRD Assumption A-3 ("`claude mcp list` is available in the devcontainer and its exit code reflects connectivity") is invalidated by the substitution; the replacement assumption (Claude Code CLI on PATH in the devcontainer) is already satisfied by the existing `claude-code` Feature. **Recommendation:** option (a) — rewrite AC-FR-5-a/b/c. **Owner:** design-composer (rewrites the AC text in the Blueprint); finalize-acceptance-test-author (re-derives EARS form if the AC text changes).

- **Q-CICD-10 (stale-calibration banner in `postCreate.sh`).** The FR-4c CI cron forces a weekly invocation of the FR-4b calibration. As a belt-and-braces defence against the trap the user named ("nobody invokes it for six months"), `postCreate.sh` could emit a banner when the most recent `calibration_result` event in `.claude/runtime/mcp-events.jsonl` is older than N weeks (suggested N = 4, giving one missed cron of grace). The banner alerts the maintainer at devcontainer rebuild time that the CI cron has been silent. The mechanism — reading the events file, computing event age, conditional warn — lives in `postCreate.sh`, which is Codespaces-layer. **Recommendation:** route to design-codespaces to decide whether to add the banner now or hold it for a follow-on feature; the CI cron alone may be sufficient for v1. **Owner:** design-codespaces; design-composer arbitrates if cross-layer coordination is needed.

- **Q-CICD-11 (ADR-0037 event-surface schema extension for `calibration_result`).** The FR-4b script emits a `calibration_result` event to `mcp-events.jsonl` per the FR-4 design. ADR-0037's canonical event-type enum may not currently include `calibration_result`. If the ADR's schema is closed-set, an additive extension is required (add `calibration_result` to the allowed types; downstream consumers ignore unknown types per ADR-0037's forward-compatibility posture, so the addition is backward-safe). If the ADR's schema is open-set / extensible-by-convention, the new type slots in without an ADR amendment. The question is which posture ADR-0037 takes today. This is a cross-layer Codespaces+CI/CD concern: the event is emitted by the Codespaces-side script but motivated by the CI/CD cadence, and the schema is a Claude-Code-layer artifact. **Recommendation:** design-composer reads ADR-0037 and either (a) confirms the schema is extensible-by-convention, no ADR change needed, or (b) files a small additive amendment to ADR-0037 (or a sibling ADR) that names `calibration_result` as a valid event type. **Owner:** design-composer (reads ADR-0037); design-claude-code (authors the amendment if (b)).

## Dependencies

Captured in the companion JSON at `cicd-dependencies.json`. The headline dependencies (`tight` binding):

- **CI/CD ← Codespaces (FR-5 image fidelity):** the devcontainer image (with `claude-code` Feature, pinned Claude Code version) must produce a working `claude --bare -p noop --output-format stream-json` invocation. If the image changes such that this invocation fails at startup, the smoke degrades from "MCP-state check" to "smoke-itself check." Cross-layer contract: the devcontainer image must include a functional Claude Code CLI on PATH; the postCreate flow must install the four OSS-local MCP servers (Serena, actionlint-mcp, terraform-mcp, GitNexus) and run auth probes against the two HTTP servers (Context7, Exa); and `.mcp.json` must register all six servers per the invocation forms ADR-0041 prescribes. The smoke verifies all six initialize to `status: connected`.
- **CI/CD ← Codespaces (FR-4c script invocation):** the FR-4b calibration script at `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` must exist, be executable, exit non-zero on behavioral drift, name the offending grammar in its stdout, and emit a `calibration_result` event to `.claude/runtime/mcp-events.jsonl` before exiting. The FR-4c workflow's exit-code-as-contract design assumes these properties. Cross-layer contract: design-codespaces owns the script's shape; design-cicd owns the workflow that invokes it.
- **CI/CD ← Claude Code:** `.mcp.json` is the artifact under test for FR-5. If `.mcp.json` evolves to use new fields (transport types, extended env-block shapes), the smoke is silent on those as long as `system/init.mcp_servers[]` continues to be the event surface. Cross-layer contract: design-claude-code keeps `.mcp.json` shaped such that Claude Code emits `system/init.mcp_servers[]` per the SDK contract; the smoke is then automatically compatible.
- **CI/CD ← Claude Code (FR-4c event surface):** ADR-0037 owns the `mcp-events.jsonl` schema. The FR-4b script writes a `calibration_result` event; whether that type is currently allowed under ADR-0037 is Q-CICD-11. The CI workflow does not depend on the event-surface schema directly (it does not read the file), but the broader feature does — surfaced for the composer.
- **CI/CD ← upstream Anthropic / Claude Code releases:** the SDK `system/init` event and the `McpServerStatus` enum are the documented stable contract. Drift in those (theoretical) would silently invalidate the FR-5 smoke. Mitigated by Q-CICD-1 (version pinning).
- **CI/CD ← upstream GitNexus npm package (FR-4c):** the calibration's whole purpose is to detect drift in upstream GitNexus install behavior between `versions.env` pin bumps. The dependency is therefore *by design* — the CI exists precisely because this dependency exists and drifts.

`provides_to` is minimal: the workflow is a terminal sink (it gates merges; it does not produce artifacts consumed by another layer). The only output is the GitHub Actions check status, which the maintainer and GitHub UI consume.

## Open items not requiring composer action

The following are noted for completeness; the design is complete without them being resolved.

- The exact SHA pins for `actions/checkout` and `devcontainers/ci` are deferred to the implementation operator (they should pull from the release pages cited above on the implementation date, to avoid this design baking in a SHA that ages).
- The "noop" prompt string passed to `claude --bare -p`: the literal word "noop" is used in this design as a placeholder. Any short string the model will not engage with substantively works; if a future Claude Code version coerces the model to respond to "noop" with substantive content, swap in something more clearly meaningless ("ignore" or a sentinel like "smoke-test-do-not-respond"). The smoke captures `system/init` before model output is consumed, so the prompt's content is incidental.

---

End of CI/CD per-layer Design. JSON companion at `working/feature/pipeline-quickwins-hardening-r1/cicd-dependencies.json`.
