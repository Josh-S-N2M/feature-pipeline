#!/bin/bash
# Invariant 2 — Three-option enumeration (Design §7.1).
# Every architectural decision in 04-decision-frames.json has a 05-substrate-map.json entry with all three options populated.
set -euo pipefail
RUN_DIR="${1:?Usage: $0 <working/synthesis/run-id>}"

DECISIONS="$RUN_DIR/04-decision-frames.json"
MAPPINGS="$RUN_DIR/05-substrate-map.json"

[[ -f "$DECISIONS" ]] || { echo "FAIL: $DECISIONS not found"; exit 1; }
[[ -f "$MAPPINGS" ]] || { echo "FAIL: $MAPPINGS not found"; exit 1; }

# Architectural decisions only
arch_ids=$(jq -r '.decisions[] | select(.class == "architectural") | .id' "$DECISIONS" | sort)

violations=0
for did in $arch_ids; do
    # Confirm there's a mapping
    has_mapping=$(jq -r --arg id "$did" '.mappings[] | select(.decision_id == $id) | .decision_id' "$MAPPINGS")
    [[ -n "$has_mapping" ]] || { echo "VIOLATION: $did has no substrate mapping"; violations=$((violations+1)); continue; }

    # Confirm all three option keys present and have non-empty descriptions
    for opt in native adapter substrate_change; do
        desc=$(jq -r --arg id "$did" --arg opt "$opt" '.mappings[] | select(.decision_id == $id) | .options[$opt].description' "$MAPPINGS")
        if [[ -z "$desc" || "$desc" == "null" ]]; then
            echo "VIOLATION: $did missing $opt option description"
            violations=$((violations+1))
        fi
    done
done

if [[ $violations -eq 0 ]]; then
    echo "PASS: invariant 2 (three-option enumeration; $(echo "$arch_ids" | wc -l | tr -d ' ') architectural decisions checked)"
    exit 0
else
    echo "FAIL: $violations enumeration violations"
    exit 1
fi
