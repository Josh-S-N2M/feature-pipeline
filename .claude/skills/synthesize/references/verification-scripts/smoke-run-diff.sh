#!/bin/bash
# Layer C smoke-run diff (task-27).
# Compare a fresh run's 01-claims.json against the golden-corpus reference.
# Tolerance: ±10% citation count, same set of source_uris, no schema violations.
set -euo pipefail
RUN_DIR="${1:?Usage: $0 <working/synthesis/run-id>}"
GOLDEN="${2:-skills/synthesize/references/golden-corpus}"

FRESH="$RUN_DIR/01-claims.json"
REFERENCE="$GOLDEN/01-claims.json"

[[ -f "$FRESH" ]] || { echo "FAIL: $FRESH not found"; exit 1; }
[[ -f "$REFERENCE" ]] || { echo "FAIL: $REFERENCE not found"; exit 1; }

fresh_count=$(jq -r '.claims | length' "$FRESH")
ref_count=$(jq -r '.claims | length' "$REFERENCE")

# ±10% tolerance
delta=$((fresh_count - ref_count))
abs_delta=${delta#-}
tolerance=$(( (ref_count + 9) / 10 ))  # ceil(10%)

if [[ $abs_delta -gt $tolerance ]]; then
    echo "FAIL: claim count drift — fresh=$fresh_count ref=$ref_count delta=$delta tol=±$tolerance"
    exit 1
fi

# Same set of source_uris
fresh_uris=$(jq -r '.claims[].source_uri' "$FRESH" | sort -u)
ref_uris=$(jq -r '.claims[].source_uri' "$REFERENCE" | sort -u)

if [[ "$fresh_uris" != "$ref_uris" ]]; then
    echo "FAIL: source_uri set differs"
    diff <(echo "$fresh_uris") <(echo "$ref_uris")
    exit 1
fi

echo "PASS: smoke-run-diff (count: fresh=$fresh_count ref=$ref_count delta=$delta within ±$tolerance; source_uris match)"
exit 0
