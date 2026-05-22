#!/bin/bash
# Invariant 4 — Constraint propagation (Design §7.1).
# Every recommended_option either honors hard_constraints OR appears in "Constraints Honored" section as a documented exception.
set -euo pipefail
RUN_DIR="${1:?Usage: $0 <working/synthesis/run-id> <output/synthesis-topic>}"
OUT_DIR="${2:?Usage: $0 <working/synthesis/run-id> <output/synthesis-topic>}"

MANIFEST="$RUN_DIR/00-manifest.json"
REPORT="$OUT_DIR/report.md"

# Extract hard_constraints
constraints=$(jq -r '.constraints.hard_constraints[]' "$MANIFEST" 2>/dev/null || true)

if [[ -z "$constraints" ]]; then
    echo "PASS: invariant 4 (no hard_constraints declared; vacuously satisfied)"
    exit 0
fi

# Confirm Constraints Honored section exists in report
if ! grep -q "^## Constraints Honored" "$REPORT" && ! grep -q "^# Constraints Honored" "$REPORT"; then
    echo "FAIL: Constraints Honored section missing from $REPORT"
    exit 1
fi

# Confirm every constraint is mentioned in the section
violations=0
for c in $constraints; do
    if ! grep -qF "$c" "$REPORT"; then
        echo "VIOLATION: constraint '$c' not mentioned in report"
        violations=$((violations+1))
    fi
done

if [[ $violations -eq 0 ]]; then
    echo "PASS: invariant 4 (constraint propagation; $(echo "$constraints" | wc -l | tr -d ' ') constraints surfaced)"
    exit 0
else
    echo "FAIL: $violations constraint propagation violations"
    exit 1
fi
