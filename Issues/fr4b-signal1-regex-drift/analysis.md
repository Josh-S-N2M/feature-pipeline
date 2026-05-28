---
id: ANALYSIS-fr4b-signal1-regex-drift
version: 0.2.0
doc_type: issue-analysis
status: complete
since: 2026-05-26
resolved_by: gitnexus-removal-ADR-0066-2026-05-27
resolved_at: 2026-05-27
resolution_summary: Resolved by removal rather than repair. The 2026-05-27 gitnexus removal (ADR-0066) eliminated the only consumer of the FR-4b calibration mechanism. Path B3 of the three remediation paths the analysis enumerated — *drop the calibration mechanism entirely; recognize that the env var doesn't actually need verifying because nobody is using it* — is now the applied disposition by virtue of gitnexus's removal. The FR-4b script was never committed to disk and the FR-4c CI workflow was never authored (Phase 3 T3.2 did not land in the shipped quickwins deliverable); ADR-0058 (calibration_result event type) is superseded by ADR-0066; the `calibration_result` schema entry is removed from audit_op7_events_schema.py; the calibration_result documentation is removed from KB-mcp-platform/references/mcp-events-jsonl.md and KB-mcp-design/references/principles.md.
feature_slug: pipeline-quickwins-hardening-r1
generated: 2026-05-26
generated_by: claude (main agent) — dogfood capture during pipeline-quickwins-hardening-r1 execution at Phase 2 → Phase 3 boundary
companion_artifacts:
  - working/feature/pipeline-quickwins-hardening-r1/integration-smoke-fr4-end-to-end.md
  - working/feature/pipeline-quickwins-hardening-r1/research-notes/t-001-gitnexus-grammar-skip-contract.md
  - working/feature/pipeline-quickwins-hardening-r1/synthesis/04-decision-frames.json
  - working/feature/pipeline-quickwins-hardening-r1/codespaces-design.md
  - .claude/runtime/mcp-events.jsonl
  - adrs/ADR-0066-gitnexus-removal.md
  - adrs/ADR-0058-calibration-result-event-type-additive-extension.md
---

## Resolution (added 2026-05-27)

The 2026-05-27 gitnexus removal (ADR-0066) made the entire FR-4b mechanism moot. Path B3 of the analysis's three remediation paths — drop the mechanism — is the applied disposition. The mechanism never had a non-gitnexus consumer; without gitnexus there is nothing to calibrate.

Concrete cleanup performed at closure:

- **ADR-0058** — status moved Accepted → Superseded by ADR-0066. The `calibration_result` event type was preserved for hypothetical future calibration mechanisms; the closed-enum discipline still applies if such a mechanism is ever introduced, but the existing schema and KB documentation are removed because they referenced the retired FR-4b path.
- **`audit_op7_events_schema.py`** — `calibration_result` schema entry removed. If a future calibration mechanism is added, the schema entry is re-introduced via a new ADR.
- **`KB-mcp-platform/references/mcp-events-jsonl.md`** — the `calibration_result` documentation section removed. Cross-references to ADR-0058 updated to note its superseded status.
- **`KB-mcp-design/references/principles.md`** — the `calibration_result` bullet and the mechanism-namespace discriminator paragraph removed.
- **`.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh`** — confirmed not present on disk (Phase 2 T2.4 never reached commit, or was removed during the gitnexus cleanup pass).
- **FR-4c CI workflow** — confirmed not present in `.github/workflows/` (Phase 3 T3.2 did not land; `mcp-connectivity-smoke.yml` is FR-5, not FR-4c).
- **`.claude/runtime/mcp-events.jsonl` line 21** — the one historical `calibration_result` event (the failed 2026-05-26 smoke) is left in place as append-only audit history per ADR-0037.
- **Feature working dir artifacts** — `working/feature/pipeline-quickwins-hardening-r1/` retains its FR-4b artifacts (integration-smoke-fr4-end-to-end.md, T-001 research note, etc.) as historical record of the shipped feature run.

The four open questions in the analysis ("which path?", "if Path A...", "if Path B...", "EBADENGINE warning") are subsumed by the removal: no path was selected because the consumer was eliminated; the EBADENGINE Node-version concern is no longer load-bearing because the gitnexus install is gone.

---

# FR-4b Calibration Contract Diverges from the Install Path the Devcontainer Actually Uses

## TL;DR

The FR-4b calibration mechanism authored during `pipeline-quickwins-hardening-r1` Phase 2 returned `outcome: drift_detected` on its first live execution at T2.5 against `gitnexus@1.6.5` — the same version T-001 research targeted at design time. The mechanism executed correctly; the divergence is real and is a contract problem, not a regex problem.

Two findings drove the verdict:

- **Signal 1 (stderr regex):** the expected `[tree-sitter-{dart,proto}] Skipping build (GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1)` messages do not appear in the live npm-install stderr. **Not because the regex is too tight — because the messages don't exist on the npm-distributed path at all.**
- **Signal 3 (artifact absence):** the `tree_sitter_{dart,proto}_binding.node` files are present under `node_modules/gitnexus/.../build/Release/` even when `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` is set.

Together these mean: **the env var is a no-op on the install path the devcontainer actually uses.** T-001 research read the GitHub-source `build-tree-sitter-{dart,proto}.cjs` files (which DO honor the env var if they run). But the npm-distributed package ships the `.node` artifacts pre-built in the tarball, so the build scripts don't run on `npm install -g gitnexus`. The contract FR-4b verifies is real for the GitHub-tag-source-build path; it is meaningless for the npm-install path the devcontainer uses.

This is structurally the same defect class the parent feature exists to prevent: ADR / research prescribes a contract, implementation diverges, no audit caught the divergence until execution time.

## Background / Evidence

### §1 — T2.5 integration smoke verbatim output

Source: `working/feature/pipeline-quickwins-hardening-r1/integration-smoke-fr4-end-to-end.md` and `.claude/runtime/mcp-events.jsonl` line 21 (the `calibration_result` event).

The event payload:

```json
{
  "event": "calibration_result",
  "timestamp": "2026-05-26T20:23:25Z",
  "server": "gitnexus",
  "mechanism": "fr-4b-gitnexus-grammar-skip",
  "version": "1.6.5",
  "duration_ms": 52376,
  "outcome": "drift_detected",
  "signals": {
    "signal_1": "drift_detected: Neither tree-sitter-dart nor tree-sitter-proto skip messages found in stderr. Upstream format may have changed.",
    "signal_3": "fail: Artifact(s) unexpectedly present: dart=2 proto=2",
    "negative_assertion": "pass: Both artifacts present in default install (dart=2 proto=2)"
  },
  "note": "Neither tree-sitter-dart nor tree-sitter-proto skip messages found in stderr. Upstream format may have changed."
}
```

The script's mechanics worked: one well-formed event written, OP-7 admits it, Q-CS-1b banner correctly silent at <14-day threshold, scratch directories cleaned up.

### §2 — Captured regex vs. live npm-install stderr

The regex in `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh`:

```
\[tree-sitter-(dart|proto)\] Skipping build \(GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1\)
```

This regex was derived from T-001 research findings F-1 and F-2, which read the upstream source at `gitnexus/scripts/build-tree-sitter-{dart,proto}.cjs` lines 5–14 of the v1.6.5 GitHub tag.

The actual stderr captured at execution time (re-confirmed on 2026-05-26 by running `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1 npm install --prefix <scratch> gitnexus@1.6.5 2>&1` directly):

```
npm warn EBADENGINE Unsupported engine {
npm warn EBADENGINE   package: 'gitnexus@1.6.5',
npm warn EBADENGINE   required: { node: '>=22.0.0' },
npm warn EBADENGINE   current: { node: 'v20.20.2', npm: '10.8.2' }
npm warn EBADENGINE }
npm warn deprecated boolean@3.2.0: Package no longer supported. ...
```

That is the entirety of the stderr. No `Skipping build` lines. No `tree-sitter` lines. The build scripts the regex targets are not producing any output on this install path.

### §3 — Artifacts present despite env var

The script's signal_3 check found `tree_sitter_dart_binding.node` and `tree_sitter_proto_binding.node` present under `node_modules/gitnexus/.../build/Release/` (count: 2 each) even with `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` exported in the environment.

This is the load-bearing finding. The env var is supposed to suppress those builds. The artifacts are present. The env var did nothing observable on this install path.

### §4 — EBADENGINE engine-mismatch warning

The npm stderr also flagged `gitnexus@1.6.5` requires Node ≥22, but the devcontainer's Node Feature provides Node 20. npm proceeded despite the warning. It is plausible the `postinstall` script that runs `build-tree-sitter-{dart,proto}.cjs` was silently skipped due to the engine mismatch — but it is also plausible (and more consistent with the artifacts being present) that the npm tarball simply ships the pre-built `.node` files and the build scripts only matter when you build from source.

The Node engine mismatch is itself a separate concern worth surfacing — the devcontainer is running a Node version the gitnexus package considers unsupported.

## Root Cause

The contract the FR-4b script verifies is defined against the GitHub-tag-source-build path of GitNexus:

- Clone the tag.
- Run `npm install` from the cloned tree.
- The `postinstall` script triggers `build-tree-sitter-{dart,proto}.cjs`.
- Those scripts read `GITNEXUS_SKIP_OPTIONAL_GRAMMARS` and either build the `.node` files or skip with an explicit stderr message.

The install path the devcontainer actually uses is different:

- `npm install -g gitnexus@1.6.5` against the npm-published package.
- npm downloads the published tarball.
- The tarball ships pre-built `.node` files.
- Either the `postinstall` script doesn't run (engine mismatch, npm config, or other reason), or it runs and finds the artifacts already present (skips the build silently without emitting the captured stderr messages).
- The env var has no observable effect.

The synthesis stage's D-0006 decision frame did discuss this fragility — it called for a looser regex (`GITNEXUS_SKIP_OPTIONAL_GRAMMARS.*[Ss]kip`) anchored on the env-var name + the word "skip", explicitly because upstream output could drift. The `codespaces-design` v0.3.0 revision tightened to per-grammar capture for at-least-once-per-grammar assertion. The tightening is not the load-bearing cause of this finding — even the loose regex would not match the actual stderr, because the actual stderr contains no skip-related output at all.

## Implications

- **The FR-4b mechanism currently verifies a contract that is not active on the install path the project uses.** The script will continue returning `drift_detected` on every invocation until the contract is redesigned or the install path is changed.
- **The FR-4c CI workflow that wraps the calibration script (Phase 3 T3.2) will fail every run** on the same drift_detected outcome, because the workflow uses the script's exit code as its pass/fail signal. This needs explicit acknowledgement when T3.2 lands.
- **T-001's research was rigorous against the GitHub source but did not account for npm-distribution-time transformations.** The research note's "drift modes" enumerated regex fragility but did not enumerate "the install path the devcontainer uses doesn't run these scripts at all." This is a research-scope gap worth recording.
- **The Q-CS-1b stale-calibration banner mechanism is still useful** even if the underlying calibration is broken — the banner detects whether the calibration has been *run recently*, which is independent of whether the calibration is *meaningful*. The banner is on solid ground.
- **The pipeline-quickwins-hardening-r1 feature run itself is not blocked.** The FR-4b mechanism works as designed (it caught a real divergence, written one event, exited non-zero). The divergence the script caught is an upstream-contract problem, not a script defect.

## Recommendations / Open Questions

Three remediation paths surfaced, each with different cost shapes:

### Path A — Change the install method

Move the devcontainer's GitNexus install from `npm install -g gitnexus@1.6.5` to something that forces the GitHub source build to run — e.g., `npm install -g git+https://github.com/abhigyanpatwari/GitNexus.git#v1.6.5` (install from the GitHub tag directly) or a `git clone + npm install` flow.

- **Effect:** the postinstall build scripts run; the env var has observable effect; FR-4b's contract becomes active and verifiable.
- **Cost:** changes ADR-0041's install-mechanism prescription for GitNexus; this is a substantive amendment, not a prose tweak. Also slows codespace build (no pre-built tarball; full source build per rebuild).
- **Trade-off:** restores the contract FR-4b was designed for; trades faster install for verifiable behavior.

### Path B — Redesign FR-4b's contract

Accept that the env var is a no-op on the npm path and rescope the mechanism. Options inside this path:

- (B1) Drop signal_1 entirely; verify only signal_3 (artifact presence) — but make signal_3's semantics "artifacts ARE present at known paths" (i.e., the artifacts work; that's the contract). The env-var-honor question disappears.
- (B2) Replace the calibration with a different upstream-behavior check that IS observable on the npm path — e.g., "the pre-built `.node` files load and respond to a known query" (a runtime smoke against the installed package).
- (B3) Drop the calibration mechanism entirely; recognize that the env var doesn't actually need verifying because nobody is using it. Remove FR-4b and FR-4c.

- **Cost:** PRD revision; Blueprint revision; ADR-0058 revision or retirement; rework of the FR-4b script and FR-4c workflow.
- **Trade-off:** preserves the install speed of the npm path but admits that the original design's assumption about the env var was wrong on the relevant install path.

### Path C — Hybrid: keep mechanism, document non-meaningful state

Leave the calibration script and FR-4c workflow in place. Mark the `drift_detected` outcome as the expected steady state until either Path A or Path B lands. Treat FR-4c's failing CI runs as deferred-MAJOR rather than blocking.

- **Cost:** smallest immediate cost; defers the real decision to a follow-on feature run.
- **Trade-off:** the pipeline-quickwins-hardening-r1 deliverable ships with a known-broken sub-mechanism. The mechanism's *presence* still serves as a tripwire (any change in stderr format or artifact behavior will be detected by future calibrations).

### Open questions for the future feature run

1. **Which path?** A, B, or C? A and B are mutually exclusive; C is interim only.
2. **If Path A:** does ADR-0041 amendment count as in-scope of a follow-on feature, or does it require its own ADR-amendment cycle?
3. **If Path B:** does the rescoped FR-4b still warrant ADR-0058's event-type extension, or does the calibration_result event type retire alongside the mechanism?
4. **Independent of the path:** the EBADENGINE warning indicates the devcontainer's Node version (20) doesn't satisfy gitnexus's declared engine requirement (≥22). Even if the env-var contract doesn't matter on the npm path, the engine-version drift is its own concern and should be surfaced.

## Cross-links

**Evolution cross-links (per ADR-0046):**

- `escalates_from`: (none — root analytical capture)
- `escalated_to`: (none yet — when a future feature run is opened, this file will be amended)

**State vocabulary (per ADR-0050):** `open` — real systemic finding awaiting future remediation; not currently being worked.

**Related files:**

- `working/feature/pipeline-quickwins-hardening-r1/integration-smoke-fr4-end-to-end.md` — T2.5 smoke verbatim record
- `working/feature/pipeline-quickwins-hardening-r1/research-notes/t-001-gitnexus-grammar-skip-contract.md` — T-001's GitHub-source findings
- `working/feature/pipeline-quickwins-hardening-r1/synthesis/04-decision-frames.json` — D-0006 framing (looser-regex original recommendation)
- `working/feature/pipeline-quickwins-hardening-r1/codespaces-design.md` v0.3.1 — where the per-grammar regex tightening landed
- `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` — the live script
- `.claude/runtime/mcp-events.jsonl` line 21 — the actual `calibration_result` event
- `adrs/ADR-0041-install-mechanism-hybrid.md` — the install-mechanism prescription that Path A would amend
- `adrs/ADR-0058-calibration-result-event-type-additive-extension.md` — the event-type extension that Path B might retire

---

*End of analysis. Report-only. No artifacts changed by this document.*
