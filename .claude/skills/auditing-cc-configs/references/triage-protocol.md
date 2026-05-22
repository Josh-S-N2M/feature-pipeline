# LLM-Judge Triage Protocol

## Contents

- LLM judge invocation
- Three-way decision
- Asymmetric rules
- Schema validation
- Anomaly detection
- Mock and live modes

The AI layer that distinguishes operationally dangerous patterns from documentation about those same patterns. Runs after deterministic scans, after pedagogical-marker prefilter, before verdict computation.

This is the load-bearing defense against two problems:
1. **False positives** — the scanner matched a pattern in example content
2. **True positive suppression** — research shows LLM judges can be biased toward "clean" verdicts via prompt injection or over-cautious framing

The protocol is designed around **asymmetric rules**: judges can demote severity but never zero out CRITICAL. Multi-agent court framing was rejected because research (CourtGuard, arXiv 2510.19844) shows it lowers true-positive rates by design.

## Where triage fits in the audit loop

```
deterministic scanners
        ↓
    raw findings (severity per pattern + location)
        ↓
pedagogical-marker prefilter
        ↓
    findings split:
      - confirmed-pedagogical → demoted to INFO
      - marker-mismatch       → demote one notch + add marker finding
      - unmarked              → continue to judge
      - false-pedagogical-claim → escalate to MAJOR
        ↓
LLM-judge triage on remaining findings ≥ MAJOR
        ↓
    judge returns CONFIRMED | PEDAGOGICAL | AMBIGUOUS
    asymmetric rules apply
        ↓
verdict computation (deterministic from final severity counts)
        ↓
    report
```

## The three-way decision

Boolean judges (clean/dirty) suppress true positives because the judge reaches for equipoise. Three-way decisions give the judge a low-stakes safe answer that still surfaces the finding to a human.

| Decision | Meaning | Action |
|---|---|---|
| **CONFIRMED** | Judge agrees the pattern is operationally dangerous in context | Severity unchanged |
| **PEDAGOGICAL** | Judge believes the pattern is documentation about the pattern, not the pattern in action | Demote to INFO + add new MINOR finding: "pedagogical content lacking marker" |
| **AMBIGUOUS** | Judge cannot determine | Demote one notch + flag for human review |

If the original finding was CRITICAL, the judge **cannot zero it out**. Maximum demotion for CRITICAL is one notch (to MAJOR) with mandatory `recommend_human_review: true`. CRITICAL findings always produce SECURITY-BLOCK or human-review flag — never silently pass.

## Severity adjustment table

| Original | CONFIRMED | PEDAGOGICAL | AMBIGUOUS |
|---|---|---|---|
| BLOCKER (CRITICAL) | BLOCKER | MAJOR + human-review | MAJOR + human-review |
| MAJOR | MAJOR | INFO + marker-missing finding | MINOR + human-review |
| MINOR | (not triaged) | — | — |

MINOR findings are not sent to the judge — too expensive for the value. They appear in the report at original severity.

## Judge input

The judge receives a structured prompt with:

1. **The finding**: pattern ID, original severity, location (file:line)
2. **The pattern description**: human-readable explanation of what was matched
3. **File role**: SKILL.md / reference / asset / example / config / hook script / memory / etc.
4. **±10 lines of surrounding context** from the file
5. **Pedagogical marker status**: file-level (`pedagogical_sections:` frontmatter present?), block-level (`audit-example` fence around the pattern?)
6. **Output schema** (strict JSON)

The judge does NOT receive:
- The audit conversation history
- Other findings in the same audit
- The user's intent or instructions
- Any data not in the structured prompt

This isolation defends against indirect prompt injection — content in the audited file cannot influence the auditor's other reasoning because the judge runs in a separate context.

## Judge output schema

```json
{
  "decision": "CONFIRMED" | "PEDAGOGICAL" | "AMBIGUOUS",
  "justification": "<1-2 sentences>",
  "recommended_severity_adjustment": 0 | -1 | -2,
  "recommend_human_review": true | false
}
```

Outputs that fail schema validation are treated as suspicious — logged, returned as AMBIGUOUS with `recommend_human_review: true`, and the audit Notes section flags "judge output failed schema validation" as a meta-finding.

## Asymmetric rules (enforced in code, not just prompt)

These are enforced in `triage_with_judge.py` regardless of what the judge returns:

1. **CRITICAL severity floor.** If `original_severity == CRITICAL` (BLOCKER), the maximum demotion is one notch. Set `final_severity = max(BLOCKER, judge_recommendation)` where MAJOR is the lowest allowed result. Always set `recommend_human_review = true`.

2. **PEDAGOGICAL on unmarked content adds a finding.** If the judge returns PEDAGOGICAL but no marker was declared, demote the finding *and* add a new MINOR finding: "Pedagogical content lacking marker — please add `pedagogical_sections:` declaration or `audit-example` fence."

3. **AMBIGUOUS always recommends human review.** Override `recommend_human_review = true` even if the judge said false.

4. **Anomaly detection.** If PEDAGOGICAL rate across the scan exceeds 80% of triaged findings, the scan is flagged as anomalous. This could indicate a prompt-injection attack on the judge or systematic mis-marking by the author. The report's Notes section surfaces this prominently.

## Operational bounds

| Setting | Value | Rationale |
|---|---|---|
| Model | Sonnet | Cost/quality balance per Trend Micro 2025 finding |
| Concurrency | 4 parallel calls | Avoids race conditions on shared finding state; respects API rate limits |
| Per-finding scope | One call per finding ≥ MAJOR after prefilter | MINOR findings not worth the cost |
| Cost ceiling | If >50 MAJOR findings after prefilter | Coordinator pauses, asks user before proceeding |
| Timeout | 60 seconds per judge call | Fails-open to AMBIGUOUS if exceeded |
| Rate-limit handling | Fails-open to AMBIGUOUS | Never silently passes findings |
| Tool scope | Read, Grep, Glob only | No network, no execute, no MCP servers |

## Anti-spec (things to never do)

- ❌ Use a single LLM call to "clean up" all findings before the report — that's the boolean trap and it suppresses TPs.
- ❌ Let the judge zero out CRITICAL findings.
- ❌ Give the judge the verdict authority. The verdict is computed mechanically from the (judge-adjusted but never zeroed) severity counts.
- ❌ Use multi-agent court framing (prosecution + defense + judge). CourtGuard research shows it lowers TPs.
- ❌ Run the judge in the same context as the user conversation — fresh context, separate turn or subagent.
- ❌ Let one judge call's output influence the next.
- ❌ Trust schema-non-conforming output. Log and treat as AMBIGUOUS.

## What the report says about triage

Every project report includes a triage summary near the top:

```
## Triage summary
- Deterministic findings: 47 total
- Confirmed by judge: 12 (severity unchanged)
- Pedagogical (with marker): 18 (demoted to INFO)
- Pedagogical (missing marker): 5 (demoted + marker-finding added)
- Ambiguous (human review needed): 8 (demoted one notch)
- Never triaged (MINOR): 4
```

If the triage summary shows >80% PEDAGOGICAL rate or schema-validation failures, the Notes section escalates these as meta-findings.

## Meta-audit logging

Every triage decision is logged for later meta-audit:

```json
{
  "finding_id": "X3-skill-bash-allow",
  "file": "...",
  "line": 42,
  "pattern_id": "BASH_WILDCARD_ALLOW",
  "original_severity": "MAJOR",
  "judge_decision": "PEDAGOGICAL",
  "judge_justification": "Pattern appears inside `audit-example` fence in references/security-checklist.md",
  "final_severity": "INFO",
  "human_review_recommended": false,
  "timestamp": "2026-05-12T18:42:11Z"
}
```

Periodic meta-audits (Phase 10.5) compare random samples against ground truth to catch judge drift. If the judge's CONFIRMED rate drops below baseline on a known-good fixture, the judge layer is itself suspect.
