# Audit Working Checklist

Copy this into your working response when auditing. Check off each item as you finish it. The list helps you survive context-window summarization in long audits — if your conversation gets summarized, the unchecked items reveal where to resume.

## Pre-flight (steps 1–3)

- [ ] **1. Target identified.** Path confirmed. Type (project / single-target) noted. If single-target, primitive type (skill, subagent, hook, etc.) noted.

- [ ] **2. Mode determined.** Default, `--managed`, or `--with-runtime` based on user intent.

- [ ] **3. Sub-skill availability checked.** For project audits, note which of the six sub-skills are installed. Missing sub-skills will appear as "skipped" in the report.

## Deterministic layer (steps 4–6)

- [ ] **4. `audit_target.py` run.** Walked the target. Each found file dispatched to its primitive's auditor. Raw findings collected.

- [ ] **5. Read flagged files.** For every finding at MAJOR or BLOCKER, the cited file was opened. Surrounding context read before promoting to the report.

- [ ] **6. Verification step applied.** Each script-derived MAJOR/BLOCKER tested against the property the script asserts. False positives dropped with note. (This is the non-negotiable step — see audit-rubric.md.)

## Cross-file layer (step 7)

- [ ] **7. `cross_file_checks.py` run.** All 24 pair checks executed. Findings merged into the pool. None silently skipped.

## Triage layer (steps 8–9)

- [ ] **8. `pedagogical_marker_check.py` run.** Findings with full marker demoted. Marker-mismatch findings emitted. Anti-laundering checked against declared sections.

- [ ] **9. `triage_with_judge.py` run.** All findings still at MAJOR or above triaged. CRITICAL findings never zeroed (verified by checking final_severity). Anomaly flag checked (>80% PEDAGOGICAL rate).

## Scoring layer (step 10)

- [ ] **10. `verdict_compute.py` run.** Score computed deterministically from final severities. Verdict applied per thresholds. SECURITY-BLOCK override checked.

## Report assembly (steps 11–17)

- [ ] **11. Critical section composed.** All SECURITY-BLOCK and confirmed-CRITICAL findings surfaced at the top of the report.

- [ ] **12. Per-component table built.** Each audited target listed with its score and verdict (project audit only).

- [ ] **13. Cross-file section composed.** Each fired check from X1–X24 listed with severity, location, fix.

- [ ] **14. Per-dimension scores listed.** All 10 dimensions per target, with the dimension number, name, score, and "status" indicator.

- [ ] **15. Memory subsections composed.** Auto memory and subagent memory each have their own section in the project report, even if no findings (state the status clearly).

- [ ] **16. Notes section composed.** Disclosed false-positive classes from the verification step. Triage anomaly flag if set. Any sub-skill missing from install.

- [ ] **17. Next actions composed.** Concrete, prioritized fix list. Each item has a file path, the operation, and the expected outcome.

## Final (step 18)

- [ ] **18. Report saved.** `audit-report-<target-name>.md` written to the current working directory. No files modified inside the audited tree.

---

## Skipping policy

If a step is genuinely not applicable (e.g., no pedagogical_sections declared → step 8's anti-laundering check finds nothing → step still applies, marked done with "0 findings"). Do not skip a step just because there's nothing to report from it — record "0 findings" or "N/A" with reason instead.

## When to copy this into a response

For audits expected to take more than 5 turns of reading and finding extraction. Short audits don't need the checklist overhead. The cost of the checklist is 18 lines of context; the value is recoverable state across summarization.
