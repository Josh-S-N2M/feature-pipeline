# Technology-evaluation pilot — observability backend, RE-RUN (RUN OUTPUT, for review)

> **✅ RESOLVED 2026-05-30 — the human picked GreptimeDB.** The workflow ended too-close-to-call between Jaeger (84) and GreptimeDB (78); the deciding question — *traces-only forever, or keep the door open to metrics/logs?* — was answered **"keep the door open,"** selecting **GreptimeDB**. Recorded in the plan (WS-4); ADR pending freeze-lift. Two post-run calibration fixes applied (do not affect the choice): TB9 scope-corrected so a backend's internal binary store isn't screened (Parseable was unfairly cut — technology-boundaries.yaml v1.3.0); and the enumeration discipline now seeds prominent LLM-observability vendors explicitly (LangSmith/Langfuse were missed — both would be eliminated on TB1 anyway).

> Output of `technology-evaluation` re-run 2026-05-29 (run wf_2c8af13e-e0e; 73 agents, ~2.8M tokens) on the **corrected** inputs: hardened rubric v1.2.0 (OTel-only standard-shape, capability re-anchored to our questions, two-way-door weight modifier, decision rules) AND TB1 v1.2.0 (tunable budget — real default 4-core/16 GB). Report-only; nothing written to canonical, ADRs, or the plan. Supersedes the first pilot record (technology-evaluation.PILOT-OUTPUT.md).

## Frame

- **Role:** A self-hostable, single-container backend that ingests the OpenTelemetry standard into a durable local store, kept off the pipeline's critical path: the pipeline must complete with it down. Artifact lineage is NOT its job — that is served by the freshness gate's in-git derived_from graph. (No vendor named.)
- **Decision class:** two-way door
- **Effective weights (hedge + two-way-door modifier):** maturity_trajectory 22, standard_shape 18, reversibility 12, operability 16, capability_fit 18, durability_fit 6, licensing_cost 5, docs_support 3

*Frame note:* Door type: two-way. Reversal is cheap by design — the backend sits behind the JSONL-of-record, never on the critical path, and lineage lives in git, so nothing load-bearing accumulates inside it; swapping = re-point OTLP export + re-stand a container, with history replayable from JSONL. Reversal-to-implementation cost ratio is low. Caveat: reversibility decays — if retained traces/dashboards/queries ever become load-bearing, re-judge door-type on a later run. Binding TBs are the service-class set: TB1 (single-container/no-compose; footprint is a flagged cost dial), TB2 (git system-of-record; volume is cache only), TB3 (no mandatory external service), TB9 (text-first/diffable, applies_to all), TB10 (credential indirection), TB11 (OTel-shaped self-hosted, OTLP-only ingest — do NOT screen on OpenLineage). Excluded: TB4/TB6/TB7 (orchestration), TB5/TB8 (libraries). Effective weights = hedge-moving-target base + two-way-door modifier (reversibility -6, capability_fit +6), net-zero, sums to 100. Sensitivity note for Score phase: top criterion is maturity_trajectory (22); shift it +/-10% per decision_rules to check rank stability.

## Eliminations (boundary screen)

### SigNoz — TB1 (mechanical)
**Reason:** SigNoz requires docker-compose with multiple interdependent services (app + ClickHouse + ZooKeeper + collector), violating TB1's hard single-container / no-docker-compose structural rule.

**Evidence:** SigNoz's only supported self-host install is Docker Compose with multiple interdependent containers. The official docker-compose.yaml (github.com/SigNoz/signoz/blob/main/deploy/docker/docker-compose.yaml) defines separate services — signoz (app), clickhouse (storage), zookeeper-1 (coordination), otel-collector, init-clickhouse, and signoz-telemetrystore-migrator — wired together with depends_on edges (signoz/otel-collector depend on clickhouse; clickhouse depends on zookeeper-1). The official Docker install docs (signoz.io/docs/install/docker/) instruct "ensure that Docker Compose is installed" and run `docker compose up`. There is no single-container install path; the candidate's own one-liner concedes "storage is a separate ClickHouse service rather than a single container."

### Uptrace — TB1 (mechanical)
**Reason:** Fails TB1's hard structural rule: it is not a single self-contained container and its self-host path is docker-compose/k8s-based, not a pip/binary single-container tool — a structural fail independent of machine size.

**Evidence:** Uptrace's install docs (https://uptrace.dev/get/install.html) and GitHub repo (https://github.com/uptrace/uptrace) confirm it requires separate backing datastores — ClickHouse (telemetry) + PostgreSQL (metadata) + Redis (caching/sessions) — and its self-hosted path ships a docker-compose.yml with a Kubernetes Helm chart as an alternative. The candidate's own one_line concedes it is "ClickHouse-backed (separate store, not a single self-contained container)."

### Parseable — TB9 (mechanical)
**Reason:** Parseable's system-of-record storage format is binary Apache Parquet, which violates TB9's text-first/diffable requirement (and TB11's JSONL-of-record framing); the binary format is confirmed from the candidate description and docs, so this is an evidenced mismatch, not an uncertainty.

**Evidence:** Parseable's defining architecture stores all ingested data as Apache Parquet — a binary columnar format — on local disk or S3 (confirmed by the candidate one-liner "storing Apache Parquet on local disk or S3-compatible object storage" and by Parseable docs: storage modes are `local-store` writing to P_FS_DIR / `s3-store`, with Parquet as the on-disk format; https://www.parseable.com/docs/environment-variables and https://github.com/parseablehq/parseable). TB9's signal is "output / artifact format (binary or proprietary vs text-diffable?)" and rules_out "binary / proprietary ... formats." TB11's constraint further specifies the observability backend should be "JSONL-of-record" (text-first, diffable); Parseable's record format is binary Parquet, not JSONL.

### HyperDX — TB2 (mechanical)
**Reason:** HyperDX keeps its durable record in external datastores (ClickHouse for telemetry, MongoDB for application state) on mounted volumes that are the system-of-record, not cache — violating TB2's requirement that git/files be the durable record and mounted volumes be cache only.

**Evidence:** ClickStack all-in-one docs (clickhouse.com/docs/use-cases/observability/clickstack/deployment/all-in-one): the image bundles "ClickHouse, HyperDX, OpenTelemetry (OTel) collector ... MongoDB (for persistent application state)." Durable state lives in those datastores on mounted volumes — "/data/db (MongoDB data), /var/lib/clickhouse (ClickHouse data)" — and "data will be lost if the container is removed or restarted unless users mount the required file paths." The GitHub repo (github.com/hyperdxio/hyperdx) confirms ClickHouse + MongoDB as the backing stores and MIT license.

## Cost flags (in-bounds, needs bigger machine)

None — all survivors fit the 16 GB default.

## Scoring (survivors), with chain-of-thought

| Rank | Tool | Total |
|---|---|---|
| 1 | Jaeger | 84 |
| 2 | GreptimeDB | 78 |
| 3 | OpenObserve | 72.3 |
| 4 | Arize Phoenix | 66.3 |

### Jaeger — 84

- **maturity_trajectory = 3** — Jaeger is a CNCF GRADUATED project (the foundation's top maturity tier), created by Uber and donated to CNCF, with very broad industry adoption as the de-facto open tracing backend. v2 is a current major release rebuilt on the OpenTelemetry Collector framework; the latest tagged release is v2.18.0 dated 2026-05-13 (16 days before today), and the docs site shows a steady per-release cadence (2.17, 2.18, plus an active 2.dev). Maintainer health is visibly strong (active issue triage with maintainer responses, e.g. the SPM-MCP feature issue #8409). This is the anchor-3 case: broad adoption + strong momentum + healthy maintainers.
- **standard_shape = 2** — Jaeger v2 IS an OpenTelemetry Collector distribution: it ingests OTLP natively over gRPC (4317) and HTTP (4318), and GenAI semantic-convention spans are just OTLP spans/attributes, which Jaeger stores and renders as-is with no custom semconv mapping. That cleanly meets anchor 2 (ingests OTLP + OTel GenAI semconv natively). It cannot reach anchor 3, however, because that level requires broad signal coverage across traces/metrics/logs, and Jaeger is structurally a TRACES-ONLY store — it has no native metrics or logs storage (its SPM/RED-metrics feature requires an external Prometheus or Elasticsearch). For THIS project that traces-only scope is fine (TB11/D-OBS-2 deliberately ingests OTel traces only and models everything as the span tree), but the rubric anchor for level 3 is the literal traces/metrics/logs breadth, which Jaeger does not have. Clean level 2.
- **reversibility = 2** — The architecture's system of record is the in-git append-only JSONL run-event log; the backend is a downstream projection fed by a small OTLP-export script (D13/§18). Jaeger is a pure OTLP consumer on the ingest side, so swapping it for any other OTLP backend is just re-pointing that export script — no proprietary ingest format to migrate off. The stored Badger files are Jaeger-internal, but since the durable record is the JSONL (replayable into any OTLP sink), exit cost is near-zero on the data side. The read side (Jaeger's query API/UI) is Jaeger-specific, so anything built directly on it would be rebuilt on a swap — that keeps it from the anchor-3 'zero migration' case. This is anchor 2: swappable behind our JSONL-of-record, open (OTLP) schema. Note: this is a two-way door, so the rubric's decision_class_modifiers would shift weight off reversibility onto capability_fit (-6/+6).
- **operability = 3** — The all-in-one role is a single Go binary in one container that combines collector + query + UI; with the Badger backend it embeds its own on-disk store, so there is NO external database and NO docker-compose for the core single-node deployment. Start is one `docker run` exposing OTLP ports plus a mounted volume; documented resource footprint is ~512Mi-1Gi memory, trivially inside the 16 GB default Codespace machine (TB1). This is the anchor-3 case: lightweight single binary, trivial start. (The compose files in Jaeger's repo are only for the optional SPM-with-Prometheus demo, which this project does not need.)
- **capability_fit = 2** — Scored against OUR written questions, not feature breadth. trace=run / span=step: PERFECT native fit — Jaeger's core model is exactly traces composed of nested spans rendered as a DAG, which is the run/step model the architecture specifies; it renders a run as a trace and each actor/tool call as a nested span out of the box. gate.result pass/fail counts: emitted as span events/attributes; Jaeger stores and lets you search by tags/attributes per run, so per-run gate results are queryable with light work. The two genuinely cross-run/aggregate questions are the gap: cycle-time-OVER-RUNS and judge STABILITY (verdict agreement across re-runs/panels) are statistical trends ACROSS many runs, and Jaeger is a per-trace viewer — it shows duration within one trace well but does not natively aggregate or trend across traces (that is SPM/metrics territory needing external Prometheus, which the single-container budget forbids). However, the architecture explicitly assigns those aggregate questions to the JSONL run-summary projection, not to the backend; the backend's job is per-run span-tree storage and trace search, which Jaeger answers well. So it answers most of our questions (run/step model natively, per-run gate/cycle data queryable) with light custom work, with the honest caveat that cross-run trend/stability is not a native Jaeger capability. Anchor 2.
- **durability_fit = 3** — Badger gives Jaeger all-in-one a durable embedded on-disk store. Setting BADGER_EPHEMERAL=false with BADGER_DIRECTORY_VALUE/KEY pointed at a mounted volume (e.g. /badger/data on a persistent volume) makes traces survive restarts and rebuilds — exactly the TB2/D17 mounted-volume model. It also supports retention via BADGER_SPAN_STORE_TTL and Badger performs value-log GC/compaction, and backup is a documented straightforward tar of the badger directory. That clears anchor 3 (local store on a mounted volume cleanly, PLUS easy backup/compaction).
- **licensing_cost = 3** — Apache-2.0, a permissive OSS license with no seat cost and no SSPL-style caveats, and the project is governed by the CNCF (a vendor-neutral foundation) at graduated status — so no single-vendor rug-pull risk. This is the anchor-3 case: permissive + foundation-governed.
- **docs_support = 3** — Jaeger has excellent, versioned official documentation (per-release docs sites for 2.17/2.18/2.dev covering architecture, configuration, deployment, SPM, persistent storage) plus abundant third-party guides. The GitHub project shows an active, responsive community with maintainers engaging substantively on feature issues (e.g. the SPM-via-MCP discussion). Anchor 3: excellent docs + active community.

### GreptimeDB — 78

- **maturity_trajectory = 2** — Active project: v1.0.2 released 2026-05-14, two weeks before scoring date — a 1.0 GA line, not pre-release churn. The OTel trace integration landed in v0.14 (mid-2025) and GenAI semconv content is current (blog dated 2026-05-09), showing steady feature momentum. GitHub repo is the open-source 'Observability 2.0 database' with real positioning against Prometheus/Loki/ES; benchmark blogs across v0.9→v0.12→v0.14 show a sustained release cadence and active maintainers. Adoption is real but the project is young (only just reached 1.0) and not yet broad-ecosystem-standard the way Prometheus/OTel-Collector are. That is solidly 'active, steady releases, real adoption' but short of 'broad adoption + strong momentum' best-in-class. Level 2.
- **standard_shape = 3** — This is GreptimeDB's strongest axis against our narrowed criterion (OTel-only; lineage excluded per D-OBS-2). It natively ingests all three OTLP signal types — metrics (since 2023), logs, and traces (v0.14) — through a unified /v1/otlp endpoint, no proprietary format required for ingest. Critically for our use case, Greptime published a dedicated GenAI-semantic-conventions stack (blog 2026-05-09) covering gen_ai client/agent/MCP spans, events, metrics, and provider conventions — i.e. native OTel GenAI semconv with broad traces/metrics/logs coverage. That matches the level-3 anchor: 'native OTel GenAI semconv (stable-shape) with broad signal coverage.' Minor caveat: ingestion is OTLP/HTTP (not gRPC OTLP in the docs I saw) and GenAI semconv itself is still stabilizing upstream, but the conformance and signal breadth clearly clear level 3. Level 3.
- **reversibility = 2** — The role design already supplies the reversibility hedge: the backend sits behind the pipeline's stable JSONL-of-record and the in-git derived_from graph owns lineage, so GreptimeDB holds only OTel-shaped observability data. Ingest is the open OTLP standard, so re-emitting the same telemetry to a different OTLP backend is a config change, not a rewrite. The lock-in risk is the QUERY side and stored historical data: GreptimeDB's storage is its own engine and queries use SQL/PromQL, so dashboards/queries written against it would need porting and historical data would need re-export to leave. Because the durable system-of-record is git (not GreptimeDB), losing the store is low-stakes, but it is not 'fully standard, drop-in, zero migration' — there is migration effort for accumulated query assets and history. This is 'swappable behind our JSONL-of-record, open schema' (open OTLP ingest, replaceable role). Level 2.
- **operability = 3** — Runs as a single binary or single container via `./greptime standalone start` or the official `greptime/greptimedb:v1.0.2` image — explicitly no docker-compose, no multi-service requirement (the standalone bundles all roles in one process). Written in Rust, it is among the lowest-memory databases in its class (benchmarked below ClickHouse and Elasticsearch) and runs the same binary down to a Raspberry Pi / ARM edge, so footprint is comfortably within the 16 GB default machine — no cost-flag needed. Start is trivial. This matches the level-3 anchor 'lightweight single binary / pip, trivial start.' I did not find published absolute idle-RAM numbers, but the single-binary Rust design and edge-device support are strong evidence of a lightweight footprint. Level 3.
- **capability_fit = 2** — Scoring against OUR written question list, NOT general feature breadth. Our questions: gate pass/fail counts, judge stability across runs, cycle-time-over-runs, and a trace=run / span=step model. GreptimeDB is a general-purpose observability DB, not purpose-built for these exact questions. The trace=run/span=step mapping is well served: OTLP traces with a span-per-step are exactly its trace data model, and v0.14 gives a queryable table model for traces. Cycle-time-over-runs (time-series of span/trace durations) and gate pass/fail counts (aggregations over span attributes/events) are expressible via SQL/PromQL. Judge stability (variance of an eval metric across runs) is computable as an aggregate query. BUT none of these are answered out-of-the-box: we must instrument the pipeline to emit the right spans/attributes and author every query and dashboard ourselves. The DB stores and lets us query the data; it does not natively know about 'gates,' 'judges,' or 'runs.' That is the level-2 anchor exactly: 'answers most of our questions (gate results, cycle-time, run/step model) with light custom work.' It does not reach level 3 (out-of-the-box answers). Level 2.
- **durability_fit = 2** — Standalone persists to a local directory on a mounted volume cleanly — the documented Docker invocation maps `-v $(pwd)/greptimedb_data:/greptimedb_data` and the data lives in `greptimedb_data/`. It also supports object storage as an alternative sink, but no external sink is REQUIRED — local-volume durability is the default path, satisfying the role ('durable local store'). This matches level 2: 'local store on a mounted volume, cleanly.' I did not confirm first-class backup/compaction tooling that would lift it to level 3 (though LSM-style compaction is implied by its engine), so I hold at 2 on the evidence in hand. Note: in this architecture git is the system-of-record (TB2) and this store is a cache, so volume-based local persistence is the right and sufficient fit. Level 2.
- **licensing_cost = 2** — Apache-2.0 (confirmed in candidate metadata and the GitHub repo). Permissive OSS, no seat cost, no SSPL-style caveat, no rug-pull mechanic in the license itself. That clears level 2 cleanly ('permissive OSS, no seat cost'). It falls short of level-3 'permissive + foundation-governed' because GreptimeDB is vendor-led (Greptime Inc.), not governed by a neutral foundation like CNCF — single-vendor stewardship is a (small) future-direction risk even under Apache-2.0. Level 2.
- **docs_support = 2** — Documentation is solid and well-organized: dedicated docs.greptime.com pages for OTLP ingestion, standalone installation, architecture, FAQ, plus a steady stream of technical blogs (benchmarks, GenAI semconv guide, Grafana Alloy best practices). The install/getting-started path is clear and the OTel integration is documented per signal type. I did not independently verify GitHub issue responsiveness, so I cannot confirm the 'active community' half of the level-3 anchor; docs alone are strong. This is a confident level 2 ('solid docs'). Level 2.

### OpenObserve — 72.3

- **maturity_trajectory = 2** — Active project: v0.90.3 released 2026-05-26 (three days before eval date), candidate flagged not-dormant. OpenObserve is a widely-known Datadog/Elasticsearch alternative with substantial GitHub adoption and steady release cadence. Backed by a commercial entity (openobserve.ai) with an enterprise edition, which signals maintainer funding and continuity. This is active with steady releases and real adoption. Not quite 'broad adoption + strong momentum' at the level of Grafana/Prometheus-scale ecosystems, but solidly meets the bar cleanly and arguably approaches best-in-class for a single-binary OTel backend.
- **standard_shape = 2** — The criterion asks how natively it ingests OTLP + OTel GenAI semconv. Evidence: 'built on OpenTelemetry standard', 'OpenTelemetry Native', 'Native OTLP' for traces/metrics/logs across all three signals — that alone clears level 2 (ingests OTLP + signals natively) and the broad signal coverage (traces/metrics/logs) points at level 3. The gap: no evidence of native OTel GenAI (gen_ai.*) semantic-convention parsing. The README tagline says 'LLM observability' but the fetch found 'no additional details about semantic conventions'. gen_ai.* attributes would still ingest as ordinary span attributes (OTLP is OTLP), so our run/step telemetry lands fine, but there is no first-class GenAI-semconv awareness. Strong broad-signal OTLP coverage; falls short of the level-3 anchor's explicit 'native OTel GenAI semconv (stable-shape)' requirement. Lands at a strong 2.
- **reversibility = 2** — Our architecture's exit design: the JSONL run-event log is the system of record; the backend is fed by a small SDK-free script that POSTs OTLP. Anything we put in via OTLP we can re-point at another OTLP backend with zero data-model migration — the backend is downstream of our system-of-record, not the keeper of it. OpenObserve stores in open Apache Parquet (readable by any DataFusion/Arrow/DuckDB tool) on local disk, not a proprietary opaque store, so even historical data is extractable. This is 'swappable behind our JSONL-of-record, open schema' = level 2. It is not fully drop-in/zero-migration at level 3 because the query layer (its SQL dialect, dashboards, alert definitions) is OpenObserve-specific and would need re-authoring on a swap, but the data path itself is clean. Note: under hedge-moving-target this is a two-way door (reversibility weight modifier -6), and the JSONL-of-record design keeps it firmly two-way. Solid level 2.
- **operability = 3** — Single Rust binary or single docker container; local mode uses an embedded SQLite meta-store + local-disk Parquet with NO external database, object store, docker-compose, or Kubernetes required (verified in quickstart docs: 'docker run -v $PWD/data:/data ...'). Setup is trivial — one container plus two env vars for credentials. Rust single-binary means a modest, dependency-free footprint; it advertises ~1/4 the hardware of Elasticsearch. This is the level-3 anchor almost verbatim: 'lightweight single binary / pip, trivial start.' The only mild caveat is it is a full observability platform (more surface than a minimal trace store), but the structural TB1 rules are cleanly satisfied with no compose/multi-node and no footprint-over-default concern. Best-in-class for our single-container constraint.
- **capability_fit = 2** — Scored against OUR written questions only, not feature breadth. Our questions: (1) trace=run/span=step nesting — OTLP traces give exactly this; agent/tool calls become nested spans, ingested natively. (2) gate pass/fail counts with severity/classification — these ride as gate.result span events/attributes; OpenObserve has no native 'gate' concept but its SQL-over-traces (DataFusion: select trace_id, duration, service_name, operation_name, custom attrs) lets us count pass/fail by querying attributes. (3) judge stability / verdict agreement across re-runs — no built-in; requires custom SQL aggregation grouping verdicts by gate across runs. (4) cycle-time-over-runs — SQL aggregation over span durations grouped by run; doable but custom. So: it answers most of our questions (the run/step model natively; gate results, cycle-time, judge-stability via light-to-moderate custom SQL and dashboards). Nothing here is purpose-built for our gate/judge-stability vocabulary — it is a general OTel backend we project our questions onto. That is precisely the level-2 anchor: 'answers most of our questions (gate results, cycle-time, run/step model) with light custom work.' Not level 3 (nothing is out-of-the-box for gate-result/judge-stability semantics), not level 1 (the run/step model and SQL queryability genuinely cover most questions). Level 2.
- **durability_fit = 3** — Our requirement: local persistent store on a mounted volume, no external sink required. OpenObserve local mode writes Parquet to a local data dir mounted as a volume (ZO_DATA_DIR=/data with -v $PWD/data:/data), embedded SQLite metadata — clean fit for 'local store on a mounted volume.' Beyond that, Parquet is a compressed columnar format with strong compression (8x-40x), it has built-in retention/compaction handling, and Parquet files are trivially backed up by copying the directory. That 'local volume + easy backup/compaction' is the level-3 anchor. Best-in-class for our durability model.
- **licensing_cost = 1** — Core/community edition is AGPL-3.0 (OSS, no seat cost), self-hostable. There is a separate proprietary Enterprise Edition under a commercial license. AGPL is a copyleft license with network-use obligations — for a self-hosted internal observability backend that we do not redistribute or offer as a service, the AGPL obligations are practically non-binding, and there is no seat cost. But it is not permissive (the level-2 anchor says 'permissive OSS'), it is not foundation-governed (single-vendor with an open-core enterprise tier, which carries a mild rug-pull / feature-gating risk), and AGPL is exactly the kind of 'OSS with caveats' the level-1 anchor names alongside SSPL. AGPL copyleft + single-vendor open-core puts this at level 1.
- **docs_support = 2** — Evidence shows a structured documentation site (openobserve.ai/docs) with quickstart, ingestion guides (OTLP/OTEL collector), deployment guides for single-node and HA, plus a maintained blog with technical how-tos (distributed tracing, OTel guides). The project has an active GitHub presence with regular releases, implying issue activity. This is solid docs with reasonable support — meets level 2 cleanly. I did not directly measure issue-response time, so I stop short of level 3 ('excellent docs + active community') on available evidence, but the documentation breadth and currency are clearly there.

### Arize Phoenix — 66.3

- **maturity_trajectory = 3** — Evidence: last release arize-phoenix-v16.3.0 on 2026-05-27 with daily commits; the candidate metadata marks it a non-dormant provisional incumbent. Arize AI is an established vendor; Phoenix is the reference OSS backend for OpenInference and is widely cited across observability comparisons (MLflow top-5, Laminar alternatives, multiple deploy guides). High release cadence, real adoption, healthy single-vendor maintainer. This is the lead lever in the active hedge-moving-target profile. Broad adoption plus strong, sustained momentum plus a healthy maintainer org puts it at the top anchor.
- **standard_shape = 1** — The criterion asks how natively it ingests the OpenTelemetry standard: OTLP plus OTel GenAI semconv (gen_ai.*). Evidence: Phoenix exposes native OTLP collectors (HTTP on 6006, gRPC on 4317) so OTLP ingest is first-class. BUT its native semantic convention is OpenInference (openinference.* / llm.* namespaces), which predates and is complementary to the OTel gen_ai.* semconv. As of 2026 the two namespaces are converging and OpenInference instrumentations emit both sets for back-compat, but Phoenix is not a pure native OTel GenAI-semconv store; it is OpenInference-flavored with gen_ai.* convergence in progress. That is squarely 'OTLP ingest, but a custom/OpenInference semconv mapping is in play' rather than 'ingests OTLP + OTel GenAI semconv natively' cleanly. The convergence-in-progress nudges it toward the top of level 1, but it does not yet meet the stable-shape native-gen_ai bar. Scored 1.
- **reversibility = 2** — The architecture keeps the backend strictly off the critical path and behind a stable JSONL-of-record: the pipeline emits an append-only JSONL log as the system of record and a small SDK-free script POSTs it via OTLP to the backend (governed-pipeline-architecture.md:487). So the backend is a downstream OTLP sink, swappable for any other OTLP-compatible store (Jaeger, Grafana, etc. per the OpenInference docs) without touching the system of record. Phoenix stores in its own SQLite/Postgres schema and exposes REST/GraphQL export, so there is some egress effort, but because our JSONL-of-record is authoritative and OTLP is the wire format, swapping it is a two-way door with minimal migration. ELv2 does not constrain internal self-host swapping. Meets 'swappable behind our JSONL-of-record, open ingest' = level 2. Not level 3 (its internal store schema is proprietary-shaped, so it is not a zero-migration drop-in if you needed to extract history from Phoenix itself).
- **operability = 2** — Evidence: runs as a genuine single container (docker run -p 6006:6006 -p 4317:4317 arizephoenix/phoenix:latest); SQLite is the zero-config default with a single volume mount at the working dir for persistence; docker-compose is explicitly optional, only for co-managing other services. No multi-node/k8s requirement. This satisfies TB1's hard structural rule cleanly. Footprint is not documented in the official deploy page, but Phoenix is a Python+SQLite single process of modest weight (no JVM, no separate broker required for the basic deployment). Simple start, single container, modest footprint = level 2. Withholding level 3 because the exact memory footprint is undocumented (cannot confirm the 'lightweight single binary / pip, trivial' top anchor with the rigor the rubric wants), and it ships as a container image rather than a single static binary.
- **capability_fit = 2** — Scored against OUR four written questions, not feature breadth. (1) trace=run / span=step: native — Phoenix is OTel-span-native and renders nested agent/tool spans, a direct fit. (2) cycle-time-over-runs: native-ish — latency per span/trace and experiment comparison across runs are first-class, so 'where did cycle time go' is answerable. (3) gate pass/fail counts with classification/severity: NOT a native Phoenix concept — gate.result events would land as custom span attributes or annotations and be aggregated with custom queries (light-to-moderate custom work via the REST/GraphQL API). (4) judge stability — verdict agreement across re-runs / order-swaps / panel members (R20): this is the weakest fit. Phoenix has human/LLM annotations and experiment compare, but the search evidence explicitly found NO built-in inter-rater / verdict-agreement / stability aggregation; this metric must be computed by us off exported annotations. So Phoenix answers two of four natively and the other two only with custom work, the harder of which (judge stability) has no native primitive. That is 'answers most of our questions with light custom work' but the judge-stability gap keeps it off a clean 2-with-confidence; I land at level 2 because the run/step and cycle-time questions (the load-bearing observability questions) are answered natively and the gate-result/stability questions are achievable through documented annotation+API surfaces, just not turnkey. Not level 3: it does not answer all four out of the box.
- **durability_fit = 2** — Evidence: SQLite default persists to a mounted volume (PHOENIX_WORKING_DIR + volume), and Postgres is supported for a production-grade store. This cleanly meets 'local store on a mounted volume' — the architecture's requirement (point the backend's persistent store at a mounted persistent volume, governed-pipeline-architecture.md:486). Level 2. Not level 3: no easy first-class backup/compaction story is documented for the SQLite path (the docs note SQLite has limited concurrent writes and recommend Postgres for production), so the 'easy backup / compaction' top anchor is not clearly met.
- **licensing_cost = 1** — Evidence: Phoenix is Elastic License 2.0 (ELv2), source-available not OSI-permissive. Free for internal self-hosting (exactly our use), no seat cost. The only restriction is you may not offer Phoenix as a hosted/managed service to third parties — irrelevant to an internal pipeline. This is the 'OSS with caveats' class (the rubric names SSPL; ELv2 is the same source-available caveat family). Not level 2 (not permissive OSS like Apache/MIT) and not level 0 (no seat cost, no rug-pull on internal self-host, no proprietary lock). Level 1.
- **docs_support = 2** — Evidence: extensive official documentation (arize.com/docs/phoenix self-hosting, deployment, license, evals, annotations cookbooks), an active GitHub with discussions and triaged issues, and a community forum. Solid, well-organized docs plus a responsive, active community. This sits at the top of level 2 toward level 3. I score 2 cleanly; reserving level 3 only because the docs had gaps on exact footprint and internal storage schema in my checks, indicating depth is good but not exhaustive.

## Verification (nested research-and-verify)

Here is the synthesis.

---

## Consensus, in plain English

All three candidates are credible, actively maintained, self-hostable single-container backends that ingest OpenTelemetry over OTLP into a durable local store. They differ in scope, license, and how cleanly they meet the "single container with a local durable disk" shape.

- **Jaeger** is the most mature (CNCF graduated, Apache-2.0, monthly releases). But it is **traces-only by design** — its OTLP receiver explicitly rejects metrics and logs. Its default single-container "all-in-one" uses in-memory storage that is lost on restart; durable local persistence requires explicitly selecting the embedded Badger backend with ephemeral mode off. It accepts OTLP over both gRPC (4317) and HTTP (4318).
- **GreptimeDB** is a unified store for metrics, logs, and traces (Apache-2.0, first GA April 2026). It runs as one container in standalone mode with a mounted local volume — the cleanest fit for "single container, durable local disk." Caveat: trace ingestion is **OTLP/HTTP only** (gRPC trace intake into Greptime itself is not offered; gRPC requires an intervening Collector).
- **OpenObserve** is also unified (logs/metrics/traces/RUM), single-binary, native OTLP, very high release cadence. Its open-source edition is **AGPL-3.0** (copyleft) — the key license distinction versus the other two. Its design is object-storage-first; local disk is supported and is the single-node default, so durable-local works but is not the headline mode.

For the stated use — ingest standard OTLP off the critical path, lineage handled elsewhere — **GreptimeDB and OpenObserve fit the "any-signal, durable-local, single-container" shape most directly. Jaeger fits only if traces are the sole signal** and you accept the Badger configuration step.

On GenAI: the OTel GenAI semantic conventions are **experimental ("Development"), not stable**. None of the three offers first-class GenAI handling; all store `gen_ai.*` as ordinary OTLP attributes. A traces-only store like Jaeger cannot retain prompt/completion **content**, which now lives in the log/event channel, not span attributes.

## Settled vs contested

| Settled (multiple verified sources) | Contested / one source flags a conflict |
| --- | --- |
| Jaeger: CNCF graduated, Apache-2.0, Go, v2.18.0 (2026-05-13), traces-only | OpenObserve "latest release" version — see could-not-verify |
| GreptimeDB: Apache-2.0, Rust, v1.0 GA (2026-04-08), single-container standalone with local volume | OpenObserve license: marketing blog says Apache-2.0; repo LICENSE says AGPL-3.0 — **AGPL-3.0 is authoritative** |
| OpenObserve: AGPL-3.0 OSS + commercial Enterprise, Rust, native OTLP, single-binary | Jaeger Badger "ephemeral default" detail — true for Jaeger, but not on the cited v2.18 page |
| OTel GenAI semconv is experimental, not stable | OpenObserve free-tier cap: 50 GB/day (pricing/EULA) vs 200 GB/day (homepage) — vendor self-contradiction |

## Confidence per major claim (load-bearing = verified citations only)

- **High** — Jaeger maturity, Apache-2.0, traces-only scope, OTLP gRPC+HTTP, v2.18.0 recency.
- **High** — GreptimeDB Apache-2.0, Rust, v1.0 GA, single-container-with-local-volume, all-three-signals over OTLP/HTTP.
- **High** — OpenObserve AGPL-3.0 (OSS) + commercial Enterprise, native OTLP, single-binary, active maintenance.
- **High** — OTel GenAI semconv is experimental; content lives in events/logs, not span attributes.
- **Medium** — Jaeger durable-local needs Badger with ephemeral disabled (true, but partly sourced from sibling/v1 docs, not the cited page).
- **Low/vendor-stated** — all adoption figures (GreptimeDB Li Auto / OceanBase; OpenObserve 6,000+ orgs / 2 PB/day) are first-party, not independently audited.

## Could-not-verify — do NOT rely on these

1. **OpenObserve "latest release v0.70.3 (2026-04-05)" — REFUTED.** Actual latest is v0.90.x (v0.90.3, 2026-05-26). Two citations carried the stale version; the platform-description parts are fine, the version/date are not.
2. **OpenObserve is Apache-2.0 (marketing blog) — REFUTED** by the repo LICENSE (AGPL-3.0). Treat AGPL-3.0 as authoritative.
3. **Jaeger Badger page asserting "ephemeral/tmpfs default + `--badger.ephemeral=false`" — UNVERIFIED on the cited v2.18 page** (the flag/default is real but lives in package/v1 docs, not that URL).
4. **Jaeger storage-page citation to `jaegertracing/jaeger/.../2.13/storage` — 404 (wrong repo path).** Underlying claim is mostly right, but ClickHouse as a native backend is v2.18, not v2.13.
5. **OpenObserve "110 contributors"** — could not be confirmed (GitHub contributor panel did not load).

Note: GreptimeDB's "OTLP/gRPC for traces was *removed*" framing is unconfirmed as a removal event — sources show traces are HTTP-only, not that gRPC was dropped.

## Draft decision record

I have all the context. The two-way door, the swap path (re-point OTLP export + re-stand a container), the JSONL system-of-record, WS-4 plan home, and the re-evaluation trigger conventions. Now I'll write the draft ADR.

A note on the sensitivity check: the top weighted criterion is maturity_trajectory at 22. Jaeger scores level 3, GreptimeDB level 2. Shifting maturity_trajectory ±10% would *widen* Jaeger's lead (it's Jaeger's strongest relative axis), so it does not flip the ranking — but the gap is 6, under the 10-point too-close-to-call band, so I must not crown a numeric winner regardless.

Here is the draft decision record.

---

# ADR-00NN — Self-hosted OpenTelemetry backend: choose a single-container OTLP store (DRAFT — too close to call between Jaeger and GreptimeDB)
Status: Proposed (DRAFT — write-freeze in effect; ratify as ADR when freeze lifts) · Date: 2026-05-29 · Decision class: two-way door

## Context & role

The pipeline needs **"a self-hostable, single-container backend that ingests the OpenTelemetry standard into a durable local store, kept off the pipeline's critical path: the pipeline must complete with it down."** Its job is to receive the run-event telemetry the pipeline emits over OTLP and let a human ask *what did this run actually do* — which stages ran, which gates passed or failed, where time and tokens went.

Artifact lineage is explicitly **not** this backend's job. Provenance lives in git, in the freshness gate's `derived_from` graph (D-OBS-2); we borrow OpenLineage's run-lifecycle vocabulary to *shape* that view but run no OpenLineage service. So this decision scores standard-shape on OpenTelemetry alone.

The system-of-record is the in-git append-only JSONL run-event log. The backend is a downstream projection fed by a small SDK-free script that POSTs the JSONL to an OTLP endpoint (governed-pipeline-architecture.md:487). The pipeline never depends on the backend being up.

Plan home: the observability workstream (WS-4). The plan currently names a specific product but marks it explicitly open to revision (D13/D17) — this record is that revision.

## Boundaries that bind this choice

| Boundary | Why it binds this choice |
|---|---|
| **TB1** — single container, no docker-compose; default 4-core/16 GB, footprint a tunable cost dial | The backend must run as one container inside the devcontainer. Multi-service stacks fail structurally regardless of machine size. |
| **TB2** — git is the system-of-record; mounted volumes are cache only | Durable state lives in git/JSONL. A backend whose own datastore is the system-of-record violates this; its local volume must be a replayable cache. |
| **TB3** — no mandatory external/cloud service on the critical path | The pipeline must complete with the backend down. SaaS-only or critical-path backends are out. |
| **TB9** — text-first, diffable formats | The system-of-record is JSONL; a backend whose *record* format is binary/proprietary conflicts with the JSONL-of-record framing (this eliminated Parseable's Parquet record). |
| **TB10** — credential indirection only | Any auth to the backend goes through env-block / Codespaces Secrets, never argv/URL/committed files. |
| **TB11** — OTel-shaped, self-hosted single-container, JSONL-of-record, no WORM; OTLP-only ingest | The dominant boundary. Screen on OTLP ingest only — do **not** screen on OpenLineage (lineage is git's job per D-OBS-2). |

Excluded as not-applicable: TB4/TB6/TB7 (orchestration), TB5/TB8 (libraries). This is a service, not a validator or library.

## Candidates considered (enumerated 2026-05-29 — recency stamp)

Eight self-hostable OpenTelemetry backends were enumerated so a re-run can diff against this set: **Jaeger, GreptimeDB, OpenObserve, Arize Phoenix** (scored survivors) and **SigNoz, Uptrace, Parseable, HyperDX** (eliminated at the boundary screen). The category is crowded and moving — a re-run must re-discover the current set rather than trust this list.

## Boundary eliminations

| Candidate | Eliminated by | Reason |
|---|---|---|
| **SigNoz** | TB1 (mechanical) | Only supported self-host path is Docker Compose with multiple interdependent containers (app + ClickHouse + ZooKeeper + collector + migrators wired by `depends_on`). No single-container install exists. |
| **Uptrace** | TB1 (mechanical) | Requires separate backing datastores (ClickHouse + PostgreSQL + Redis); self-host path is docker-compose / Helm, not a single self-contained container. |
| **Parseable** | TB9 (mechanical) | System-of-record storage format is binary Apache Parquet, not text-diffable — conflicts with TB9 and TB11's JSONL-of-record framing. |
| **HyperDX** | TB2 (mechanical) | Durable record lives in external datastores (ClickHouse + MongoDB) on mounted volumes that *are* the system-of-record, not cache — violates TB2. |

All four eliminations are mechanical (structural facts confirmed from official install docs / repos), not judgment calls.

## Scoring (survivors)

Weights for this decision: hedge-moving-target base plus the two-way-door modifier (reversibility −6, capability_fit +6, net zero), summing to 100. Top criterion is maturity_trajectory (22), reflecting how fast the AI-observability category churns.

| Criterion (weight) | Jaeger | GreptimeDB | OpenObserve | Arize Phoenix |
|---|---|---|---|---|
| maturity_trajectory (22) | 3 | 2 | 2 | 3 |
| standard_shape (18) | 2 | 3 | 2 | 1 |
| reversibility (12) | 2 | 2 | 2 | 2 |
| operability (16) | 3 | 3 | 3 | 2 |
| capability_fit (18) | 2 | 2 | 2 | 2 |
| durability_fit (6) | 3 | 2 | 3 | 2 |
| licensing_cost (5) | 3 | 2 | 1 | 1 |
| docs_support (3) | 3 | 2 | 2 | 2 |
| **Weighted total (norm. 100)** | **84** | **78** | **72.3** | **66.3** |

Per-criterion chain-of-thought and abstention notes live in the Phase-4 scorecard (referenced, not inlined). No abstentions were recorded for any survivor.

**Top-two gap is 6 points, inside the 10-point too-close-to-call band.** By the decision rules this record does **not** crown a numeric winner. Jaeger and GreptimeDB are presented as too close to call; the choice between them is a judgment call described under Decision.

## Evidence & verification

Load-bearing claims, with verification status from Phase 5:

**Verified (high confidence):**
- Jaeger — CNCF *graduated*, Apache-2.0, Go, traces-only by design (its OTLP receiver explicitly rejects metrics/logs), OTLP over gRPC (4317) + HTTP (4318), latest v2.18.0 (2026-05-13).
- Jaeger durable-local works via the embedded **Badger** backend on a mounted volume — but the single-container "all-in-one" default is **in-memory and loses data on restart**; durability requires explicitly selecting Badger with ephemeral disabled.
- GreptimeDB — Apache-2.0, Rust, first GA v1.0 (2026-04-08), single-container standalone with a local volume, ingests all three OTLP signals over **OTLP/HTTP** (trace ingest is HTTP-only; gRPC traces need an intervening Collector).
- OpenObserve — **AGPL-3.0** OSS edition (the marketing-blog "Apache-2.0" claim is refuted by the repo LICENSE; treat AGPL-3.0 as authoritative) plus a commercial Enterprise tier, Rust, native OTLP, single-binary.
- OTel **GenAI semantic conventions are experimental ("Development"), not stable**. None of the candidates offers first-class GenAI handling; all store `gen_ai.*` as ordinary OTLP attributes. GenAI prompt/completion *content* now rides in the log/event channel, so a traces-only store (Jaeger) cannot retain it.

**Could-not-verify (do not rely on):**
- OpenObserve "latest v0.70.3 / 2026-04-05" — **refuted**; actual head is v0.90.x (v0.90.3, 2026-05-26). Platform description is fine; version/date are stale.
- The Jaeger Badger "ephemeral-by-default / `--badger.ephemeral=false`" detail is real but is **not on the cited v2.18 page** (it lives in package/v1 docs) — verify against current docs before relying on the exact flag.
- All adoption figures (GreptimeDB Li Auto / OceanBase; OpenObserve 6,000+ orgs / 2 PB/day) are first-party, not independently audited.

## Decision

**Too close to call — the choice is between Jaeger and GreptimeDB, and it turns on one question: traces-only forever, or keep the door open to metrics and logs?**

This record does not pick a single winner because the 6-point gap is inside the 10-point band. The two contenders represent two honest readings of the role:

- **Jaeger** (84) is the conservative, maturity-led pick. It is the most mature option on the board — CNCF graduated, Apache-2.0, monthly releases — and its native model (a trace = a run, a span = a step) is a *perfect* fit for how the architecture models a run. The price: it is **traces-only by design**, and its single-container default is in-memory, so durable-local requires the Badger configuration step. If the architecture's deliberate traces-only scope (TB11 / D-OBS-2) holds, Jaeger is the cleaner, lower-risk fit.
- **GreptimeDB** (78) is the option-preserving pick. It is the cleanest single-container-with-local-volume fit and the only contender that ingests **all three OTel signals** today, with explicit GenAI-semconv content published — so it scores highest on standard_shape. The price: it is **young** (just reached 1.0), **vendor-led** rather than foundation-governed, and trace ingest is HTTP-only.

**The deciding judgment** belongs to a human: if we are confident the backend will only ever hold traces, lean Jaeger (maturity + exact model fit). If we want headroom for metrics/logs without a future migration, lean GreptimeDB (signal breadth + clean local-volume durability).

**Runner-up and swap path (either direction).** Because this is a two-way door, the runner-up is cheap to adopt later. The backend sits behind the JSONL-of-record and lineage lives in git, so **nothing load-bearing accumulates inside the backend**. Swapping = re-point the OTLP export script at the new endpoint + re-stand one container, then replay history from the JSONL log. The only re-work is the read side (dashboards/queries built directly against one backend's query API would be re-authored). OpenObserve (72.3) is the third option, gated mainly by its AGPL-3.0 copyleft.

**Sensitivity check.** Shifting the top-weighted criterion (maturity_trajectory, 22) by ±10% does **not** flip the Jaeger-vs-GreptimeDB ranking — maturity is Jaeger's strongest relative axis (level 3 vs GreptimeDB's level 2), so raising its weight widens Jaeger's lead and lowering it narrows the gap without crossing over. The ranking is stable to that perturbation; the too-close-to-call verdict stands on the 6-point gap, not on weight fragility.

## Consequences

**What we accept.** A best-of-breed self-hostable OTel backend that runs in one container off the critical path, with run history on a mounted volume and the JSONL log as the durable record. If Jaeger is chosen: rock-solid maturity and an exact run/step model. If GreptimeDB is chosen: room for metrics and logs without a migration.

**What we give up.** Cross-run aggregate questions — cycle-time *over many runs* and judge *stability* (verdict agreement across re-runs/panels, R20) — are **not native** to any contender; the architecture already assigns those to the JSONL run-summary projection, not the backend. With Jaeger specifically we give up metrics/logs entirely and the ability to retain GenAI prompt/completion *content* (which lives in the log channel a traces-only store does not mount). With GreptimeDB we accept a young, single-vendor project and HTTP-only trace ingest.

**What we must watch.** (1) Reversibility decays — if retained traces, dashboards, or queries ever become load-bearing, the door stops being two-way and the door-type must be re-judged on a later run. (2) The OTel GenAI semconv is still experimental; attribute names can change. (3) If Jaeger is chosen, confirm the Badger durable-local config actually persists across rebuilds before relying on it.

## Re-evaluation trigger

**Hybrid — re-check when the OpenTelemetry GenAI semantic conventions leave experimental ("Development") status, OR by 2026-11-29, whichever fires first.** (6-month horizon, the default for AI-infra volatility.)

**Check mechanism (CI-enforced, preferred over a bare date):**
- *Signal* — a small CI fitness check pings the OpenTelemetry semconv spec for the GenAI conventions' stability marker; it **fails the build** when the status changes from `Development`/experimental to `Stable`. Stabilization changes the standard_shape scoring (every candidate would then be judged against a stable GenAI contract) and is the single event most likely to change the answer.
- *Backstop* — an expiry test pinned to **2026-11-29** that passes until the review date then **fails CI**, converting the date into an active signal rather than a line in a doc. This is wired alongside the periodic improvement-loop batch (D-IL-1), which also scans review dates.
- *Optional secondary* — a release-cadence watch on the chosen tool's repo could be added (no release in N months → flag), since cadence stall is the other observable that would erode the maturity_trajectory score that dominates this decision.

On fire, the workflow re-runs from Frame and supersedes this record (D-KN-3): either a re-affirmation (same choice, fresh date) or a changed choice (old marked `superseded_by`). Lineage is kept bi-temporally either way.

## Links

- **Boundaries satisfied:** TB1, TB2, TB3, TB9, TB10, TB11 (governed-pipeline-architecture.md:1048–1058).
- **Architecture role + swap path:** governed-pipeline-architecture.md:437, :485–487; decisions D-OBS-2 (:983), D13/D17.
- **Plan workstream:** WS-4 — Observability (governed-pipeline-architecture.md:908).
- **Supersedes / superseded_by:** supersedes the provisional product named in the plan (D13/D17); `superseded_by:` (none yet).

---

## What a human should sanity-check by hand before this is ratified

Before ratifying, a human should confirm the three things automation could not fully verify and the one judgment the rules deliberately left open. First, **the open decision itself**: this record stops at "too close to call" by design (6-point gap inside the 10-point band) — a person must make the traces-only-vs-keep-the-door-open call between Jaeger and GreptimeDB, because that turns on product intent (will this backend ever need metrics/logs?), not on the score. Second, **Jaeger's durable-local story**: the in-memory default loses data on restart, and the exact Badger ephemeral flag could not be confirmed on the cited current-version page — stand up the container, write traces, restart it, and confirm they survive before trusting "durable local store." Third, **the stale evidence**: the OpenObserve version data in the source material was refuted (real head is v0.90.x, not v0.70.x), so re-pull current release/maintenance facts for whichever finalist you lean toward rather than trusting the enumerated snapshot. Finally, **re-confirm the GenAI-semconv trigger is still experimental as of the ratification date** — if it has already stabilized, the standard_shape scoring is out of date and the evaluation should re-run from Frame before this record is adopted.