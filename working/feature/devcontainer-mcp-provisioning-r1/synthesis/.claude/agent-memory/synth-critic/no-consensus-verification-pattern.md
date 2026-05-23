---
name: no-consensus-verification-pattern
description: How to verify a "no consensus exists" claim — survey-set defensibility, analogue search, and adversarial framing checks
metadata:
  type: feedback
---

When a research claim asserts "no consensus exists" or "no pattern found across surveyed sources," the negative claim is verified by checking four things rather than by searching for the positive:

1. **Surveyed-set named explicitly?** The note must enumerate which source-categories were checked. If the claim is "no consensus across surveyed sources," the surveyed-set must be visible in the source. Anonymous surveys can't ground negative findings.
2. **Closest-analogue search performed?** A disciplined negative finding will name the nearest positive pattern (often from an adjacent domain) and explicitly disclaim its transferability. Absence of an analogue search is a red flag — it suggests the author didn't look.
3. **Framing appropriately bounded?** "No consensus across surveyed sources" (cautious) verifies more easily than "no pattern exists anywhere" (unbounded). Reject the unbounded form.
4. **Adversarial probe: could a positive pattern exist outside the public-literature survey?** Private vendor docs, Slack communities, internal whitepapers — these may host patterns the survey couldn't reach. Note this risk but do not let it invalidate a well-disciplined negative finding.

**Why:** Negative findings (no-consensus, no-precedent) often become load-bearing "novel design space" framings for downstream Synthesizer/Framer. If they survive scrutiny they unlock genuine design freedom; if they fail, the project copies an existing pattern unnecessarily. Verifying the discipline of the negative is what distinguishes "we didn't find it" from "it doesn't exist in this corpus."

**How to apply:** When encountering a `notes: "no-consensus finding"` or "negative finding" attribution, do not mark verified-by-default. Apply the four-checks above against the source. Verify all four pass before assigning verified/high. If only 2-3 pass, downgrade to verified/medium. If 0-1 pass, mark unverifiable.

**Worked example:** T-007 F5.4 (primary-to-fallback MCP transition surfacing). All four checks passed: 5 source-categories named, microservice circuit-breaker named as closest analogue with explicit non-transferability disclaimer, "across surveyed sources" framing properly bounded, adversarial probe accepted but does not invalidate. Verdict: verified/high.
