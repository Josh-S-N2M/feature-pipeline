#!/bin/bash
# Invariant 5 — Critic verdict integrity (Design §7.1).
# Every claim with verdict=='unverifiable' (and no dissent_evidence) is either excluded from 04-decision-frames OR surfaces in Limitations.
set -euo pipefail
RUN_DIR="${1:?Usage: $0 <working/synthesis/run-id> <output/synthesis-topic>}"
OUT_DIR="${2:?Usage: $0 <working/synthesis/run-id> <output/synthesis-topic>}"

CRITIQUES="$RUN_DIR/03-critique.json"
DECISIONS="$RUN_DIR/04-decision-frames.json"
REPORT="$OUT_DIR/report.md"

# Set of unverifiable claim ids without dissent_evidence
unverifiable=$(jq -r '.critiques[] | select(.verdict == "unverifiable" and .dissent_evidence == null) | .claim_id' "$CRITIQUES" | sort)

# Set of all claim ids referenced in decision frames
referenced=$(jq -r '.decisions[].claim_cluster_ids[]' "$DECISIONS" | sort -u)

violations=0
for cid in $unverifiable; do
    # If referenced in a decision frame: violation
    if echo "$referenced" | grep -qFx "$cid"; then
        echo "VIOLATION: $cid (unverifiable, no dissent) is in a decision_frame — should be excluded"
        violations=$((violations+1))
        continue
    fi
    # If NOT referenced AND not surfaced in Limitations section: violation
    if grep -q "^## Limitations" "$REPORT"; then
        if ! grep -qF "$cid" "$REPORT"; then
            echo "VIOLATION: $cid (unverifiable, no dissent) not surfaced in Limitations"
            violations=$((violations+1))
        fi
    else
        echo "VIOLATION: Limitations section missing AND unverifiable claims exist ($cid)"
        violations=$((violations+1))
    fi
done

if [[ $violations -eq 0 ]]; then
    echo "PASS: invariant 5 (Critic verdict integrity; $(echo "$unverifiable" | grep -c .) unverifiable claims correctly handled)"
    exit 0
else
    echo "FAIL: $violations Critic-integrity violations"
    exit 1
fi
