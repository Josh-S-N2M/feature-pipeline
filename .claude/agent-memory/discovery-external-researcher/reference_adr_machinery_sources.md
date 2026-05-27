---
name: reference-adr-machinery-sources
description: For research topics on ADR companion-file vs. NLP-parse design patterns, these sources consistently yield primary-source-quality material in a single search pass.
metadata:
  type: reference
---

For topics on ADR-as-policy, ADR enforcement, or "as-built matches as-designed" verification, the strongest source clusters surface from these search-query patterns:

- "Architecture Decision Records ... machine-checkable companion verification" — surfaces Archgate, ADR Kit (kschlt), DECIDER, adr-kit (rvdbreemen), structured-MADR (zircote). All 2025–2026 OSS projects with README-as-primary-source.
- "ArchUnit ADR rule enforcement" — surfaces TNG/ArchUnit user guide and the reflectoring.io engineering blog (Tom Hombergs).
- "Pact contract testing schema vs code" — PactFlow's three-part blog series is the canonical trade-off analysis in this space.
- "Terraform Sentinel OPA Conftest plan diff" — HashiCorp tutorial docs are primary; env0 / Spacelift / OneUptime blogs corroborate.
- For LLM-as-NLP-on-ADR-prose reliability evidence: arXiv 2602.07609 (LLM ADR compliance), arXiv 2504.08207 (DRAFT), arXiv 2405.19623 (DRMiner) — all 2024–2026, on-topic.
- For empirical case-study evidence of detection-without-removal: Rosik 2011 (Software: Practice and Experience) is the cleanest cite.

Avoid Medium articles entirely — the source-constraints disciplines exclude them, and the OSS READMEs already give richer detail. Marketing pages from "OpenAPI testing tools" vendors (e.g. Total Shift Left) corroborate well but should not be the primary cite.
