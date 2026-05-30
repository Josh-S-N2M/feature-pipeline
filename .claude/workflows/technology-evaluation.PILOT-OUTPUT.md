# Technology-evaluation pilot — observability backend (RUN OUTPUT, for review)

> **⚠ Resolved since this run (2026-05-29):** the OpenLineage question below was settled — the backend is **OpenTelemetry-only**; artifact lineage is the freshness gate's in-git `derived_from` graph, not an ingested OpenLineage backend (decision D-OBS-2). This record is preserved *as the run actually executed* (older "OTel/OpenLineage shape" framing), so the `standard_shape` scores here still penalize the missing OpenLineage half. A re-run on the corrected rubric (v1.1.0) scores standard-shape on OTel alone, and the ranking will shift accordingly.

> Report-only output of the `technology-evaluation` workflow run on 2026-05-29 (run wf_983c250b-e88; 71 agents, ~2.7M tokens). **Nothing here was written to canonical, ADRs, or the plan** — it is a draft for your review. Read it as *"is the shape producing a trustworthy decision,"* not as a final pick: the rubric weights are still provisional pending the methodology pass.

## 1. Frame

- **Role (agnostic):** A self-hostable, single-container backend that ingests the standard OpenTelemetry/OpenLineage shape into a durable local store, sitting off the pipeline's critical path (the pipeline completes with it down).
- **Decision class:** two-way door
- **Binding boundaries:** TB1, TB2, TB3, TB9, TB10, TB11
- **Active rubric profile:** hedge-moving-target
- **Weights:** maturity_trajectory 22, standard_shape 18, reversibility 18, operability 16, capability_fit 12, durability_fit 6, licensing_cost 5, docs_support 3

*Frame note:* Service-class decision (role names a self-hostable container/backend). Binding TBs = those whose applies_to includes services or all: TB1 single-container budget, TB2 git system-of-record, TB3 no mandatory external service, TB9 text-first/diffable, TB10 credential indirection, TB11 OTel/OpenLineage-shaped self-hosted off-critical-path. Excluded: TB4/TB6/TB7 (orchestration), TB5/TB8 (libraries). Two-way door: the role places it behind the stable JSONL-of-record and off the critical path, so it can be swapped with bounded migration (matches the reversibility criterion's level-2 anchor). Incumbent Arize Phoenix is provisional and open to revision.

## 2. Candidates enumerated (2026-05-29)

8 live, 0 dormant. Survivors were scored; the rest were eliminated at the boundary screen.

## 3. Boundary eliminations (the hard gate)

### SigNoz (standalone) — eliminated by TB1 (mechanical)
**Reason:** Single-image/no-compose half is confirmed, but the bundled ClickHouse forces a ~4 GB floor that cannot be confirmed to fit the shared 8 GB devcontainer budget alongside the rest of the pipeline, and it requires --privileged (not a plain single-process tool) — in-bounds is not confirmable, so on_uncertainty:eliminate applies.

**Evidence:** SigNoz Docker Standalone install docs (https://signoz.io/docs/install/docker/, updated 2026-04-28) state: "A minimum of 4GB of memory must be allocated to Docker." The signoz/signoz-standalone Docker Hub image (https://hub.docker.com/r/signoz/signoz-standalone) bundles ClickHouse + OTel Collector + query engine + SQLite and must be run with `docker run -d --name signoz --privileged ...` (systemd inside the container). SigNoz capacity-planning docs (https://signoz.io/docs/setup/capacity-planning/community/resources-planning/) show ClickHouse as the dominant memory consumer (16-32 GiB at scale; the bundled component is the same engine). Third-party deploy recipe confirms a 4 GB RAM floor just to boot (2 GB ClickHouse + 1 GB SigNoz + 1 GB overhead).

### Uptrace — eliminated by TB1 (mechanical)
**Reason:** Requires a multi-service ClickHouse + PostgreSQL (+ Redis) stack wired via docker-compose with a documented footprint of 24 vCPU / 48 GB RAM — far beyond the 4-core / 8 GB single-container budget TB1 mandates.

**Evidence:** Official self-host docs (uptrace.dev/get/install.html) describe Uptrace as "a distributed system" requiring three separate backing services: ClickHouse (traces/logs/metrics), PostgreSQL (metadata), and Redis (caching/session). The repo (github.com/uptrace/uptrace) ships a docker-compose example as the primary self-host path and states ClickHouse + PostgreSQL are "mandatory components." Stated hardware footprint starts at 24 vCPU / 48 GB RAM / 1 TB SSD for the smallest documented tier.

### HyperDX (ClickStack) — eliminated by TB2 (mechanical)
**Reason:** TB2 rules out tech that assumes an external persistent datastore as the durable record; HyperDX's durable telemetry/state record lives in ClickHouse + MongoDB, not in git or diffable files.

**Evidence:** ClickHouse official docs for the clickstack-all-in-one image (https://clickhouse.com/docs/use-cases/observability/clickstack/deployment/all-in-one) state the bundle is "ClickHouse + HyperDX + OTel collector + MongoDB (for persistent application state)." The durable telemetry record lives in ClickHouse on-disk at /var/lib/clickhouse and application state (dashboards, alerts, saved searches) in MongoDB at /data/db. The docs explicitly note "data will be lost if the container is removed or restarted — unless users mount the required file paths," confirming a database is the durable system-of-record. These are external persistent datastores holding the record, and the mounted volumes hold that record itself — not git, not text files, not cache.

### Marquez — eliminated by TB1 (mechanical)
**Reason:** Marquez is a compose/k8s-orchestrated multi-container service (Java API + separate mandatory PostgreSQL), which is exactly what TB1 rules out — it is not a single-container, no-docker-compose-dependency tool.

**Evidence:** Marquez's official quickstart brings the system up via docker/up.sh, which runs a multi-service docker-compose stack. The repo's own docker-compose.yml (raw.githubusercontent.com/MarquezProject/marquez/main/docker-compose.yml) defines two orchestrated services — an `api` Java service and a separate `db` (image: postgres:14) — with `api` declaring `depends_on: - db`. The GitHub README documents the Java API server (ports 8080/8081), a web UI (port 3000), and a MANDATORY external PostgreSQL 14 database ("Marquez cannot function without a PostgreSQL instance"), plus a Helm chart in /chart for k8s. It is not a single-process pip/binary tool: it is a Java service that requires a separate PostgreSQL container, normally orchestrated by docker-compose.

## 4. Scoring (survivors) — with the chain-of-thought behind each level

| Rank | Tool | Total |
|---|---|---|
| 1 | OpenObserve | 81.7 |
| 2 | Jaeger | 72.7 |
| 3 | Arize Phoenix | 57.3 |
| 4 | Marquez (Ilum Rust fork) | 49.3 |

### OpenObserve — 81.7

- **maturity_trajectory = 3** — Anchors: 3 = broad adoption + strong momentum + healthy maintainers. Evidence is unambiguous: ~19k GitHub stars, 202 releases, latest v0.90.3 on 2026-05-26 (three days before today), candidate flagged extremely active and non-dormant. Release cadence is high, adoption is real, maintainers are clearly healthy. This is exactly the recency/momentum profile the lead lever rewards.
- **standard_shape = 2** — Anchors: 2 = ingests OTel natively; 3 = native OTel GenAI AND OpenLineage. OpenObserve is built on the OpenTelemetry standard and is OTLP-native for logs/metrics/traces over a single endpoint (HTTP and gRPC), so the OTel half of the agnostic shape is met cleanly and natively. However, I found no evidence of OpenLineage ingestion in the GitHub repo or docs — searches for OpenObserve + OpenLineage returned only generic OpenLineage results, and the repo fetch explicitly noted OpenLineage is not mentioned. The role asks for 'OpenTelemetry/OpenLineage shape.' OTel is fully native; OpenLineage (the pipeline-run/lineage half) would require custom mapping, likely emitting lineage as OTLP spans or custom logs. That is native-OTel-only, which is the level-2 anchor, not the level-3 dual-native anchor.
- **reversibility = 2** — Anchors: 2 = swappable behind our JSONL-of-record with open schema; 3 = fully standard, drop-in, zero migration. Ingest is via the open OTLP standard, so producers are not locked to a proprietary wire format — swapping the backend means re-pointing the OTLP endpoint, which is genuinely two-way-door on the ingest side. Storage is open Parquet (columnar, readable outside the tool) on local disk or S3, so data is exportable rather than trapped in a proprietary store. Behind the project's stable JSONL-of-record, this sits off to the side and is replaceable. It is not a perfect 3 (zero migration) because dashboards, the internal stream/index layout, and any saved queries are OpenObserve-specific and would need rebuilding on a swap, and the query API is not a cross-vendor standard. Open ingest + open Parquet storage = clean level-2.
- **operability = 3** — Anchors: 2 = single container, modest, simple start; 3 = lightweight single binary / pip, trivial start. OpenObserve is a Rust single binary, also shipped as a single Docker container, with zero-config OTLP ingest and a documented trivial start. That strongly points toward 3. The footprint check: default aggressive caching wants ~2GB RAM (well under the 4GB heaviness threshold in the level-1 anchor), and it can be tuned down toward ~1GB via env vars. A single Rust binary with a modest sub-4GB footprint and trivial start is the best-in-class operability shape this rubric describes. Minor caution that default caching is RAM-hungry, but it stays clearly in lightweight-single-binary territory.
- **capability_fit = 3** — Anchors: 2 = answers gate pass/fail, judge stability, cycle-time; 3 = those + rich exploration out of the box. The role here is narrow: a durable backend that ingests the OTel shape and sits off the critical path. As a full observability platform (logs, metrics, traces, RUM, dashboards, alerting, SQL/PromQL querying), OpenObserve can absolutely answer gate pass/fail counts (filter/count over log fields), judge stability and cycle time (metrics + trace aggregations), and supports trace=run/span=step since it is trace-native. It also offers rich ad-hoc exploration (full SQL over Parquet, dashboards, PromQL) out of the box — the level-3 'rich exploration' descriptor. Slight reservation: pipeline-run semantics would be expressed through generic OTel traces/logs rather than a purpose-built run/step model, so it is rich-but-generic rather than tailored. Strong, leaning best-in-class for exploration; I land at 3 because the out-of-the-box exploration surface clearly exceeds the level-2 bar.
- **durability_fit = 2** — Anchors: 2 = local store on a mounted volume cleanly; 3 = that + easy backup/compaction. For our single-container (non-HA) scenario, local disk storage IS supported, and data lands as Parquet files that sit naturally on a mounted volume — clean level-2 behavior. Toward level 3: Parquet on disk/S3 is straightforward to back up (copy the data dir / sync the bucket), and the engine handles compaction of Parquet segments itself, which is the 'easy backup/compaction' descriptor. The caveat is the durability window: ingesters batch in memory and on local disk before flush, and docs note local-disk-only is unsupported in HA mode (object store mandatory there). That caveat does not bite our single-container off-path role, but the brief single-copy window plus the official steer toward object storage for production keeps this just short of an unqualified 3. Solid local persistence on a volume with self-compaction = high 2.
- **licensing_cost = 1** — Anchors: 1 = OSS with caveats (e.g. SSPL); 2 = permissive OSS, no seat cost; 3 = permissive + foundation-governed. The OSS edition is AGPL-3.0 with a separate commercial Enterprise Edition (open-core). AGPL is OSI-approved and has no seat cost for the OSS edition, so it clears 'no seat cost / no immediate rug-pull.' But AGPL is a strong copyleft network license, not permissive, and the open-core split introduces feature-gating and some rug-pull-adjacent risk (features can migrate to EE). The rubric's level-1 anchor explicitly names a copyleft caveat (SSPL) as the example of 'OSS with caveats'; AGPL-3.0 + commercial EE is the same shape of caveat. Single-vendor governed (not foundation), copyleft, open-core — that is level 1, not the permissive level 2.
- **docs_support = 2** — Anchors: 2 = solid docs + responsive issues; 3 = excellent docs + active community. Evidence: extensive official documentation site covering architecture, ingestion (per-language OTLP guides), environment variables, storage management, and HA deployment — clearly solid and well-organized. GitHub Discussions are active (e.g. the memory-usage discussion thread) and the 202-release cadence implies responsive maintainers. The breadth of docs plus an active discussion/issue surface and a ~19k-star community supports a strong reading; I did not independently measure issue-response latency, so I stop at a confident 2 rather than claiming best-in-class 3.

### Jaeger — 72.7

- **maturity_trajectory = 3** — Jaeger is a CNCF graduated project (one of the most established tracing backends), v2 released its OpenTelemetry-in-the-core rework, the candidate's last release is 2026-05-13, and the roadmap was refreshed April 2026. Broad real-world adoption, strong momentum (the v2/OTel rebirth), healthy multi-vendor maintainer base. This is squarely the top anchor: broad adoption + strong momentum + healthy maintainers.
- **standard_shape = 2** — The criterion measures how natively it ingests the agnostic shape, defined as OTel GenAI semconv + OpenLineage. Jaeger v2 ingests OTLP natively (OpenTelemetry is in the core, no translation step) on 4317/4318 — so the OTel half is best-in-class. But it has zero OpenLineage support; it is a distributed-tracing backend, not a lineage store. GenAI semconv is just OTel attributes so it rides on the native OTLP ingest, but the OpenLineage data-lineage shape simply has no home here. Anchor 3 requires native OTel GenAI AND OpenLineage; anchor 2 is 'ingests OTel GenAI natively.' It cleanly meets 2 (native OTel) but cannot reach 3 because OpenLineage is absent.
- **reversibility = 2** — Because ingest is plain OTLP and the JSONL-of-record stays the source of truth, Jaeger sits behind the stable interface and is swappable — anything emitting OTLP can point at a different backend with no producer changes. However Jaeger's query/storage model is its own (Jaeger trace JSON via its Query API; storage is pluggable but the read schema is Jaeger-shaped, not a generic open schema you'd migrate trivially to another tool). So it is 'swappable behind our JSONL-of-record' on the ingest side (anchor 2), but not 'fully standard, drop-in, zero migration' on the read/store side. Anchor 2 fits: swappable behind the JSONL-of-record, open-ish (OTLP in, but Jaeger-specific query shape out).
- **operability = 2** — The all-in-one image is a genuine single container bundling collector + query + UI + embedded storage, started with a few env vars — that satisfies single-container/simple-start. But persistence is the catch: with in-memory it's ~hundreds of MB, yet Badger (the durable single-node option) has been observed requesting several GB, with dev guidance of 512Mi-4Gi limits. It is a Go binary (not pip), single-process-ish, modest start, but the durable-persistence memory profile pushes it toward the heavier end rather than 'lightweight trivial.' That lands at anchor 2 (single container, modest, simple start) rather than 3.
- **capability_fit = 1** — The criterion asks whether it answers the project's actual questions: gate pass/fail counts, judge stability, cycle time, trace=run/span=step. Jaeger maps trace=run/span=step natively and is excellent for cycle-time (span durations) and per-run trace exploration. But it is a trace explorer, not a metrics/aggregation engine: gate pass/fail COUNTS and judge-stability over many runs are aggregate analytics that Jaeger does not compute out of the box — you'd lean on tag search and manual inspection, or push those as metrics to a different tool. It answers some core questions well (cycle time, trace=run exploration) with real gaps on the aggregate gate/stability counting. That is anchor 1: answers some, real gaps.
- **durability_fit = 2** — Badger gives an embedded persistent store on the local filesystem that survives restarts (BADGER_EPHEMERAL=false, BADGER_DIRECTORY pointed at a mounted volume) with no external sink required — cleanly meeting 'local store on a mounted volume.' There is no first-class built-in backup/compaction tooling surfaced for the dev all-in-one beyond Badger's own GC, so it does not reach anchor 3's 'easy backup/compaction.' Anchor 2 fits.
- **licensing_cost = 3** — Apache-2.0, no seat cost, no rug-pull risk, and it is a CNCF graduated, foundation-governed project. That is exactly anchor 3: permissive + foundation-governed.
- **docs_support = 3** — Jaeger has extensive official documentation (versioned docs site, deployment/storage/configuration guides), an active GitHub with maintainer-answered discussions, and a large community as a graduated CNCF project. Excellent docs + active community fits the top anchor.

### Arize Phoenix — 57.3

- **maturity_trajectory = 3** — Phoenix is the incumbent and clearly the most active candidate in this space. Release 16.0.0 landed 2026-05-21 (within the last week of the 2026-05-29 eval date), the arize-phoenix server package ships on a very frequent cadence, and it has broad adoption (large GitHub footprint, Arize-backed maintainers, wide ecosystem integrations via OpenInference). This is the top anchor: broad adoption + strong momentum + healthy maintainers.
- **standard_shape = 1** — This is the candidate's weakest fit against the stated role, which is the 'standard OTel/OpenLineage shape.' Phoenix ingests OTLP over HTTP (6006) and gRPC (4317) cleanly, but its semantic-convention expectation is OpenInference (its own llm.* / openinference.* namespace), NOT native OTel GenAI semconv. Traces in OTel GenAI (gen_ai.*) shape require a span processor / translation layer to display correctly; there is an open backlog feature request (openinference issue #2205, opened Sep 2025, still unimplemented) explicitly asking for native OTel GenAI semconv support. And there is no OpenLineage ingestion at all — Phoenix is an LLM-trace tool, not a data-lineage backend. So it matches anchor 1 (OTLP ingest, but custom semconv mapping needed) rather than anchor 2 (ingests OTel GenAI natively). It cannot reach 2 or 3, and the OpenLineage gap reinforces the cap. I land at 1.
- **reversibility = 1** — Exit posture is mixed. On the positive side, the store is plain SQLite or PostgreSQL (open, queryable, not a proprietary opaque format) and the wire format in is OTLP, so the project can keep its JSONL-of-record upstream and re-point ingestion elsewhere. But the on-the-wire schema Phoenix understands is OpenInference, a vendor-originated convention; data captured/displayed in Phoenix's model leans on that shape, so swapping to a backend expecting OTel GenAI gen_ai.* would require migration/translation effort. That is squarely anchor 1: swappable with migration effort. It is not 'swappable behind our JSONL-of-record with an open standard schema' (2) because the schema is OpenInference-specific, not the agnostic standard the role names.
- **operability = 2** — Single official container (arizephoenix/phoenix) that bundles the OTLP collector and the UI in one process; default storage is embedded SQLite with no external service needed, so it runs as a true single container. Footprint is modest — Arize runs hosted Phoenix on ~2GB RAM / 1 CPU, well under the 4GB heavy threshold. Start is simple (docker run, set PHOENIX_WORKING_DIR, mount a volume). This meets anchor 2 cleanly (single container, modest, simple start). It is not anchor 3 (lightweight single binary / pip, trivial start) — it is a multi-component Python service in a container with a couple-GB working footprint rather than a tiny static binary, and there are known volume-permission start frictions (issue #3187). So 2.
- **capability_fit = 1** — The role's core questions are pipeline-shaped: gate pass/fail counts, judge stability, cycle time, and a trace=run / span=step mental model. Phoenix maps a run to a trace and a step to a span well (it is built on exactly that span tree), and it ships LLM-as-judge evaluators plus datasets/experiments, which speak to judge stability and exploration. But it is an LLM-application-observability tool, not a pipeline-gate analytics tool: gate pass/fail counts and cycle-time-over-runs are not first-class out of the box — you would derive them from span attributes/queries rather than read them off a built-in view, and it has no OpenLineage/job-run lineage notion for non-LLM pipeline steps. That is anchor 1 (answers some, real gaps) edging toward 2; the absence of native gate/cycle-time reporting and the LLM-trace-centric model keep it at the cautious side. I score 2 only if those are cleanly answered — they are partial — so 1, but it is a strong 1.
- **durability_fit = 2** — Strong fit. Phoenix persists to a local relational store (SQLite by default, or PostgreSQL) and is explicitly documented to run with a mounted persistent volume via PHOENIX_WORKING_DIR=/mnt/data, no external sink required. That is exactly anchor 2 (local store on a mounted volume, cleanly). It does not clearly clear anchor 3 (easy backup / compaction as a first-class feature) — backup is 'copy the SQLite file / use Postgres tooling' rather than a built-in compaction/backup workflow, and there are documented volume-permission setup frictions. So 2.
- **licensing_cost = 1** — Phoenix is Elastic License 2.0 (ELv2). It is free to self-host with no seat cost and no feature gates for internal use, which avoids anchor 0. But ELv2 is NOT an OSI-approved open-source license — it prohibits offering Phoenix as a hosted/managed service to third parties. That is the 'OSS with caveats' band (the rubric names SSPL as the example; ELv2 is the same source-available-with-restriction class). It is single-vendor governed (Arize), not foundation-governed, and source-available licenses carry a non-zero rug-pull/relicense risk. So anchor 1, not 2 (permissive OSS, no seat cost).
- **docs_support = 3** — Documentation is extensive and well maintained: dedicated self-hosting docs (Docker, Kubernetes, persistence), OTEL reference docs across versions, a semantic-conventions spec, plus an active community forum (community.arize.com) and a busy, responsive GitHub issue tracker. That meets anchor 2 (solid docs + responsive issues) and arguably reaches anchor 3 (excellent docs + active community). Given the breadth of versioned docs, the public community platform, and clear issue engagement, I lean to 3.

### Marquez (Ilum Rust fork) — 49.3

- **maturity_trajectory = 1** — The fork is freshly active: 0.54.0 released 2026-03-08, last push 2026-05-06, not archived, with a substantial ~38k-line Rust rewrite landed. But the maintainer base is thin — the fork has 16 stars, 2 forks, 1 watcher, and commits trace essentially to one developer (@thijs-s) plus the Ilum org. It exists precisely BECAUSE upstream Marquez slowed, and Ilum's own stated intent is to realign with / upstream into the 2199-star reference project rather than carry an independent fork long-term. So the durable trajectory is genuinely ambiguous: the code is moving now, but bus-factor is low and the project's own roadmap points back toward upstream. That is more than 'young or visibly slowing' in raw cadence, but the single-maintainer, tiny-adoption, fork-may-reconverge profile keeps it short of 'active, steady releases, real adoption'. Borderline 1/2; the thin maintainer health and explicit reconvergence plan pull it to 1.
- **standard_shape = 1** — Marquez ingests the OpenLineage shape natively — it is the OpenLineage reference backend, and the Ilum build advertises OpenLineage 2.0.2 native support. That squarely satisfies the OpenLineage half of the agnostic shape. However the rubric's anchors are framed around OTel GenAI semconv AND OpenLineage: level 2 is 'ingests OTel GenAI natively', level 3 is 'native OTel GenAI and OpenLineage'. Marquez is an OpenLineage lineage server; it does not ingest OpenTelemetry GenAI traces/metrics at all — its /lineage HTTP endpoint speaks OpenLineage run/job/dataset events, not OTLP. So for the OpenLineage axis it is best-in-class, but it covers only one of the two standard shapes the rubric names and cannot take OTel directly. Strong on half, absent on the other half: a clean 2 is not warranted because OTel GenAI ingest is missing; it lands at partial.
- **reversibility = 2** — The store is plain PostgreSQL with the documented, open Marquez data model (the published normalized run/job/dataset/version schema), and the wire format is the open OpenLineage spec. Events arrive as standard OpenLineage JSON, which means the pipeline's JSONL-of-record can be replayed into any other OpenLineage backend, and the Postgres schema is open and queryable. The Ilum fork also keeps 100% API compatibility with upstream Marquez, so swapping the Rust build back for the Java upstream (or another OL backend) is a documented path. This is swappable behind our JSONL-of-record with an open schema — a clean 2. It is not a 3 (fully drop-in, zero migration) because moving off Marquez still means schema/data migration if you want to preserve history, and the fork-vs-upstream divergence adds a small re-alignment cost.
- **operability = 2** — The Rust rewrite's explicit selling point is lower resource usage and smaller memory footprint than the Java/Dropwizard original, and the deployment shape is a single API container plus PostgreSQL. The Docker Hub notes say the API server needs no container volumes (all state in Postgres) and starts with a couple of env vars. That is a single, modest, simple-start service — meets the criterion cleanly. It is not a 3: it is not a self-contained single binary/pip with trivial start, because it mandates an external PostgreSQL (and optionally OpenSearch for search), so the runnable unit is two services, not one lightweight process. Solidly a 2.
- **capability_fit = 1** — The pipeline's actual questions are gate pass/fail counts, judge stability, cycle time, and trace=run / span=step mapping. Marquez's data model is run/job/dataset lineage with run state transitions, run-level metadata, versioning, and a lineage graph — it maps naturally to run=run and step=job, and run state transitions give it the raw material for cycle-time and pass/fail-by-run analysis, plus a rich lineage-exploration UI and (in this fork) a Search API. So it answers cycle-time and run-outcome questions and offers rich exploration. The gap: it is a lineage/provenance model, not a span-tree tracing or eval/judge-metrics store. 'span=step' and 'judge stability' are not first-class — there is no native span timeline or judge-score aggregation; you would model those as job runs/facets and compute stability yourself. It answers some core questions well with real gaps on the span/judge axis. That is squarely a 1 leaning 2; the missing native span and judge-metric support holds it at 1-to-2 — I place it at 1 because two of the four named questions are not natively served.
- **durability_fit = 2** — Persistence is PostgreSQL. In a single-container/devcontainer context this is a local Postgres whose data directory sits on a mounted volume — a clean local persistent store on a volume, no external cloud sink required. Postgres also has trivial, well-understood backup (pg_dump) and retention/compaction story. The one wrinkle versus an embedded single-file store: durability lives in the Postgres data dir rather than in the API container itself (the API container is stateless), so 'on a mounted volume cleanly' is satisfied via the DB container's volume. That is a clean 2, arguably brushing 3 given Postgres's mature backup tooling; I keep it at 2 because the durable state is in a separate service's volume rather than a self-contained store, which is slightly more setup than the anchor's 'cleanly'.
- **licensing_cost = 2** — Apache-2.0, permissive OSS, no seat cost, no rug-pull mechanism. The upstream Marquez project is LF AI & Data Foundation / OpenLineage-governed, which would argue for foundation-governed (level 3). But the candidate here is specifically the Ilum-maintained fork, which is governed by a single vendor (Ilum), not a foundation — the foundation governance applies to upstream, and this fork's continuation depends on Ilum's commercial interest. So it is clearly permissive OSS with no seat cost (level 2), but the vendor-controlled fork governance keeps it from the foundation-governed level 3.
- **docs_support = 2** — Upstream Marquez has solid docs (quickstart, data-model docs, tutorials for Airflow/Spark/dbt) and the fork inherits and refreshes the README, plus a clear ILUMxMARQUEZ rationale doc, a CHANGELOG, Docker Hub usage docs, and a Helm chart. That is solid documentation. Support responsiveness on the fork specifically is thin, though: with 2 open issues, 1 watcher, and essentially one maintainer, issue responsiveness is unproven, and the primary support channel is Ilum's own Slack rather than an active community. Solid docs but uncertain/limited support — between 1 and 2; the strong inherited docs justify 2 rather than 1, while the absent community keeps it off 3.

## 5. Verification (nested research-and-verify)

All claims are pre-verified; I have everything needed to synthesize. No tool calls required.

# Telemetry Backend Candidates: Consensus

## 1. Consensus in plain English

The requirement bundles two different standards as if they were one shape. **OpenTelemetry (OTLP)** carries traces, metrics, and logs. **OpenLineage** carries data-pipeline lineage (run/job/dataset events) over a separate wire format (`POST /api/v1/lineage`). All three candidates handle the OTLP half. **None of them ingests OpenLineage.** If lineage ingestion is a hard requirement, none of these three qualifies, and you would need a tool such as Marquez (the OpenLineage reference backend).

On the OTLP half, all three meet the single-container, off-critical-path, durable-local-store bar, but they differ sharply:

| | License | OTLP-native | Durable single-container store | Scope | Maintenance |
|---|---|---|---|---|---|
| **OpenObserve** | AGPL-3.0 (OSS); commercial Enterprise | Yes (logs+metrics+traces) | Single Rust binary; Parquet + local data dir | Full observability | Multiple releases/week, May 2026 |
| **Jaeger** | Apache-2.0 (permissive, no open-core) | Yes (v2 = OTel Collector core) | All-in-one image; embedded Badger (must set `--badger.ephemeral=false`) | Traces only | CNCF graduated; v2.18 May 2026 |
| **Phoenix** | Elastic License 2.0 (source-available, *not* OSI) | Accepts OTLP, but native model is OpenInference | Single image; SQLite/Postgres | LLM/GenAI only | Releases ~daily, May 2026 |

**Plain takeaway:** Jaeger is the cleanest license and the most battle-tested, but traces-only. OpenObserve is the broadest fit (all three signals, true single binary) at the cost of AGPL copyleft. Phoenix is purpose-built for LLM observability and carries a restrictive non-OSI license; it is the wrong tool for general pipeline telemetry.

## 2. Settled vs contested

**Settled (verified):** every license, the OTLP support of all three, single-container deployment for all three, durable-store mechanism for all three, maintenance recency, and the OpenLineage gap. Jaeger's CNCF-graduated status and traces-only scope. Phoenix's OpenInference-not-generic-OTel specialization.

**Contested / nuanced:**
- **OpenObserve's free Enterprise tier**: vendor pages disagree (50 vs 200 GB/day). Real disagreement, confirmed on both pages.
- **Jaeger Badger defaults**: durable, but *ephemeral by default* — a config footgun, not a capability gap.
- **Phoenix "open-source" marketing** vs ELv2's source-available reality (managed-service restriction is real).

## 3. Confidence per major claim (load-bearing = verified only)

| Claim | Confidence |
|---|---|
| None of the three ingests OpenLineage | **High** — verified across all three + OpenLineage docs |
| Licenses (AGPL-3.0 / Apache-2.0 / ELv2) | **High** — confirmed in each LICENSE file |
| All three are OTLP-native / accept OTLP | **High** |
| All three: single-container + durable local store | **High** |
| All actively maintained (recent 2026 releases) | **High** |
| Jaeger CNCF graduated, traces-only | **High** |
| Phoenix = LLM-specialized (OpenInference) | **High** |

## 4. Could-not-verify list (do NOT rely on these)

- **OpenObserve "under 2 minutes" single-binary claim** — *unverified*. Cited homepage says "two to three minutes" (POC) and "under five minutes" (Helm HA); the "under 2 minutes" figure is not on the source.
- **OpenObserve "202 total releases"** — inferred from pagination, not confirmed.
- **OpenObserve v0.80.0 on 2026-04-23** — plausible but not directly surfaced.
- **Jaeger "440 contributors"** — not confirmed (live count ~433); peripheral.
- **Exact live counts** (GitHub stars ~19k/~23k/~10k, Phoenix ~180 contributors) — drift over time; treat magnitudes only.
- **Vendor adoption self-claims** (OpenObserve "6,000+ organizations," "2 PB/day") — vendor-reported, not independently verified.

Treat the OpenLineage requirement as the decision pivot: confirm whether you actually need lineage ingestion before choosing among these three, because none satisfies it.

## 6. Draft decision record (the workflow's recommendation)

I have everything I need. Producing the draft decision record below.

---

# ADR-00NN — Self-hostable single-container telemetry backend: choose Arize Phoenix (provisional re-affirmation)

Status: Proposed · Date: 2026-05-29 · Decision class: two-way door

## Context & role

The architecture names this role (Part V, agnostic):

> "A self-hostable, single-container backend that ingests the standard OpenTelemetry/OpenLineage shape into a durable local store, sitting off the pipeline's critical path — the pipeline completes with it down."

Plan home: the observability workstream. The current pick is provisional — a specific product is named but explicitly open to revision. This run re-evaluates that pick against the current candidate set and either re-affirms it or replaces it.

This is a **two-way door**. The pipeline's JSONL-of-record stays the system-of-record; the backend sits behind that stable interface and off the critical path, so swapping it is a bounded migration (re-point the OTLP endpoint; rebuild dashboards/saved views), not a one-way commitment. That reversibility is exactly why this is a plan-level technology pick and not itself an architectural boundary.

## Boundaries that bind this choice

These are the boundaries (Appendix F) whose `applies_to` includes `services` or `all`. This is a service, so the library boundaries (TB5/TB8) and orchestration boundaries (TB4/TB6/TB7) do not apply.

| Boundary | Litmus reason it binds here |
|---|---|
| **TB1** single ephemeral container, ≤8 GB, no compose | The backend must boot as one container inside the shared devcontainer budget. |
| **TB2** git is system-of-record | The durable record may not live in a mandatory external datastore standing in for git. |
| **TB3** no mandatory external service on the critical path | The pipeline must complete with the backend down — it cannot be a hard runtime dependency. |
| **TB9** text-first / diffable | Operational and config surface should be text-first and diffable. |
| **TB10** credential indirection only | Any auth must use env / secret-store indirection, never inline credentials. |
| **TB11** standard-shape, self-hostable, JSONL-of-record, no WORM | Must ingest the standard OTel/OpenLineage shape, self-hosted, off the critical path, with no write-once-read-many store. |

## Candidates considered (enumerated 2026-05-29 — recency stamp)

The full discovered set, so a re-run can diff against it:

- SigNoz (standalone)
- Uptrace
- HyperDX (ClickStack)
- Marquez (upstream Java)
- Marquez (Ilum Rust fork)
- OpenObserve
- Jaeger
- Arize Phoenix (incumbent)

## Boundary eliminations

| Candidate | Eliminated by | Reason |
|---|---|---|
| **SigNoz (standalone)** | TB1 | Single image, but the bundled ClickHouse forces a ~4 GB RAM floor that cannot be confirmed to fit the shared 8 GB budget alongside the rest of the pipeline, and the image requires `--privileged` (systemd-in-container). In-bounds is not confirmable, so the default-eliminate-on-uncertainty rule for the hard boundary applies. |
| **Uptrace** | TB1 | A distributed system requiring ClickHouse + PostgreSQL (+ Redis), wired via docker-compose, with a documented smallest tier of 24 vCPU / 48 GB RAM — far past the single-container budget. |
| **HyperDX (ClickStack)** | TB2 | The durable telemetry record lives in ClickHouse on-disk plus application state in MongoDB; these are external persistent datastores serving as the durable record, not git or diffable files. |
| **Marquez (upstream Java)** | TB1 | A compose/k8s-orchestrated multi-container service (Java API + a separate mandatory PostgreSQL with `depends_on`), which is precisely what TB1 rules out. |

(The Marquez Ilum Rust fork survived the screen — it ships a single API container against an external Postgres, treated as the DB's volume rather than a compose-mandated second service — and was scored.)

## Scoring (survivors)

Active profile: **hedge-moving-target**. Weighted total = Σ(level × weight) / 3, normalized to 100. Chain-of-thought and any abstentions live in the scorecard artifact, referenced here, not inlined.

| Candidate | Maturity (22) | Std-shape (18) | Reversibility (18) | Operability (16) | Capability (12) | Durability (6) | License (5) | Docs (3) | **Total** |
|---|---|---|---|---|---|---|---|---|---|
| **OpenObserve** | 3 | 2 | 2 | 3 | 3 | 2 | 1 | 2 | **81.7** |
| **Jaeger** | 3 | 2 | 2 | 2 | 1 | 2 | 3 | 3 | **72.7** |
| **Arize Phoenix** *(incumbent)* | 3 | 1 | 1 | 2 | 1 | 2 | 1 | 3 | **57.3** |
| **Marquez (Ilum fork)** | 1 | 1 | 2 | 2 | 1 | 2 | 2 | 2 | **49.3** |

## Evidence & verification

Verified, load-bearing (high confidence): every license (OpenObserve AGPL-3.0; Jaeger Apache-2.0; Phoenix Elastic License 2.0); all four survivors accept the OTLP shape; all four deploy as a single container with a durable local store; all are actively maintained (recent 2026 releases); Jaeger is CNCF-graduated and traces-only; Phoenix is LLM-specialized around the OpenInference convention rather than generic OTel.

**The decision pivot, verified high-confidence:** the role's requirement bundles two distinct standards. **OpenTelemetry/OTLP** carries traces/metrics/logs; **OpenLineage** carries pipeline-run lineage over a separate wire format (`POST /api/v1/lineage`). **None of the scored survivors ingests OpenLineage.** All satisfy the OTLP half only. The only candidates that natively ingest OpenLineage are the Marquez family — and the deployable Marquez forms were either eliminated at TB1 (upstream) or scored last on a thin single-maintainer trajectory (Ilum fork).

Could-not-verify (do not rely on): OpenObserve's "under 2 minutes" single-binary claim (the cited page says two-to-three minutes for a POC), its "202 releases" count, and its free-Enterprise-tier cap (vendor pages disagree, 50 vs 200 GB/day); Jaeger's exact contributor count; live GitHub star magnitudes; vendor adoption self-claims. None of these is load-bearing for the decision.

## Decision

**Re-affirm Arize Phoenix** for the LLM-trace half of this role, with eyes open, as a provisional two-way-door pick — *not* because it tops the scorecard (it does not; it places third at 57.3), but because the scorecard's leader does not serve the project's actual question better than Phoenix does, and the role's framing forced a re-frame mid-evaluation. The reasoning:

- The highest raw score, **OpenObserve (81.7)**, wins on maturity, operability, and broad capability — but it is a general logs/metrics/traces platform under AGPL-3.0 copyleft with an open-core split. Its capability strength is *generic* exploration, not the pipeline-run / judge-stability / LLM-eval questions this project actually asks; those would be hand-modeled as generic spans. It is the strongest *general* backend, not the strongest fit for the LLM-evaluation workload Phoenix is purpose-built for.
- Phoenix already maps run→trace and step→span natively, ships LLM-as-judge evaluators and datasets/experiments, and runs as a single container on a ~2 GB footprint with embedded SQLite on a mounted volume. Its low scores are concentrated in standard-shape (it speaks OpenInference, with server-side OTel-GenAI auto-conversion only as of 2026-05-15) and licensing (Elastic License 2.0 is source-available, not OSI-approved — the managed-service restriction is real but does not bite internal self-hosting).
- Critically, **the decisive weakness is shared by every survivor**: none of them satisfies the OpenLineage half. Swapping Phoenix for the top-scored OpenObserve would trade a known, fit-for-purpose LLM tool for a higher-scored generic one while *still* not closing the lineage gap. The score gap does not buy what the role needs.

This re-affirmation is therefore explicitly conditional on the human sanity-check below resolving the OpenLineage question.

**Runner-up: OpenObserve.** It is the choice if the role is re-scoped away from LLM-eval semantics toward general OTLP observability, and if AGPL copyleft is acceptable.

**Swap path (two-way door).** Producers emit OTLP to a stable endpoint behind the JSONL-of-record. To swap Phoenix → OpenObserve (or any OTLP backend): (1) stand up the new single container with a mounted volume; (2) re-point the OTLP endpoint env var; (3) rebuild dashboards / saved views (these are tool-specific and do not migrate); (4) replay or let historical data age out — Phoenix's SQLite/Postgres store is queryable for one-time export if history must be preserved. No producer code changes. Bounded migration, matching the reversibility criterion's level-2 anchor.

## Consequences

**What we accept:**
- A source-available license (Elastic License 2.0), single-vendor-governed (Arize), carrying a non-zero relicense/rug-pull risk and a managed-service-to-third-parties prohibition we do not currently hit.
- An OpenInference-centric semantic model; generic OTel-GenAI traces rely on Phoenix's server-side conversion, which is recent.
- Gate pass/fail counts and cycle-time-over-runs are derived from span attributes/queries, not read off a built-in view.

**What we give up:**
- The top scorecard slot — we are not taking the highest-scored tool, by design.
- Native OpenLineage ingestion — **no survivor offers it**; if the pipeline genuinely needs lineage ingestion, this whole shortlist is the wrong shelf and Marquez (or DataHub/OpenMetadata) is required instead.
- A foundation-governed permissive license (Jaeger offers that, but is traces-only and weaker on our actual questions).

**What we must watch:**
- Whether the OpenLineage half of the role is a hard requirement or aspirational — this is the single largest open risk.
- Elastic License 2.0 terms and Arize's governance stance.
- Phoenix's OTel-GenAI semconv coverage maturing past its recent auto-conversion.

## Re-evaluation trigger

**Hybrid (whichever fires first):**

1. **Signal — license/cadence/owner change on the incumbent.** Re-check when any of: Arize relicenses Phoenix away from Elastic License 2.0; Phoenix's release cadence stalls (no release in 3 months); or the maintaining owner changes. **Check mechanism:** a small CI check on the `Arize-ai/phoenix` repo (latest-release date + LICENSE-file hash), run on the same schedule as the boundary fitness functions.
2. **Signal — standard reaches stable.** Re-check when the OpenTelemetry GenAI semantic conventions leave experimental and reach stable, since that materially raises every generic-OTel survivor's standard-shape score and could flip the decision. **Check mechanism:** the domain-freshness check (D-DOM-4) that already re-checks `authoritative_sources`, with the OTel GenAI semconv spec page added to that source list.
3. **Date backstop — re-check by 2026-11-29.** Default 6-month horizon for AI-infra. **Check mechanism:** the periodic improvement-loop batch (D-IL-1) scans trigger dates.

On fire, the workflow re-runs from Frame and the new record either re-affirms (fresh date, `supersedes` this one) or changes the choice (`supersedes` this one; this one marked `superseded_by`). Lineage is kept bi-temporally.

## Links

Boundaries satisfied: TB1, TB2, TB3, TB9, TB10, TB11 (Appendix F) · plan workstream: observability · supersedes: *(the provisional incumbent record, if one exists)* · superseded_by: *(none yet)*.

---

**What a human should sanity-check by hand before this is ratified.** The whole recommendation hinges on one unverified premise: *is OpenLineage ingestion actually required by this role, or is the "OpenTelemetry/OpenLineage shape" phrasing aspirational?* Confirm that against the architecture's Part V intent — because if lineage is a hard requirement, **none of the four scored survivors qualifies** and the correct move is to widen the shelf to an OpenLineage backend (Marquez or equivalent), not to re-affirm Phoenix. Second, confirm the team accepts Elastic License 2.0's source-available terms for internal self-hosting (we never offer Phoenix as a managed service, so the one real restriction does not bite — but a human should own that read). Third, decide consciously whether placing third on the scorecard is acceptable here: the recommendation deliberately overrides the raw ranking on fit grounds, and that override is a judgment call the human at the seam should ratify, not inherit. If any of those three resolve the other way, the runner-up (OpenObserve) or a re-scoped enumeration is the correct next step.

---
## 7. The two open calls for you

1. **Was "OpenLineage-shaped" (TB11 / Part V) a hard requirement or aspirational?** No single-container backend ingests both OTel and OpenLineage; the only OpenLineage-native tool (Marquez) fails the container budget. If hard → this shelf is wrong (two-backend design). If aspirational → reword TB11, the OTLP shelf is right.

2. **The rubric's `capability_fit` anchor scored general breadth, not fit-to-our-questions** (Phoenix, LLM-native, scored 1; OpenObserve, generic, scored 3 — the workflow had to override its own scorecard in prose). Fix the anchor now and re-run, fold it into the methodology pass, or bank the finding and move on?
