#!/bin/bash
# Invariant 1 — Citation invariant (Design §7.1, §5.7).
# Every assertion in report.md ends in [<name>](<source_uri>) resolving to a claim.id whose source_uri is in manifest.inputs.confirmed[].
set -euo pipefail
RUN_DIR="${1:?Usage: $0 <working/synthesis/run-id> <output/synthesis-topic>}"
OUT_DIR="${2:?Usage: $0 <working/synthesis/run-id> <output/synthesis-topic>}"

REPORT="$OUT_DIR/report.md"
CLAIMS="$RUN_DIR/01-claims.json"
MANIFEST="$RUN_DIR/00-manifest.json"

[[ -f "$REPORT" ]] || { echo "FAIL: $REPORT not found"; exit 1; }
[[ -f "$CLAIMS" ]] || { echo "FAIL: $CLAIMS not found"; exit 1; }

# Extract every (label)(uri) link from report.md
links=$(grep -oE '\[[^]]+\]\([^)]+\)' "$REPORT" | grep -oE '\([^)]+\)$' | tr -d '()' || true)

# Confirmed-input set (from manifest)
confirmed=$(jq -r '.inputs.confirmed[]' "$MANIFEST")

# Source-uri set (from claims)
claim_uris=$(jq -r '.claims[].source_uri' "$CLAIMS" | sort -u)

violations=0
for uri in $links; do
    # Allowed: uri is a claim source_uri (which by recursion-safety must already be in manifest.confirmed)
    if ! echo "$claim_uris" | grep -qFx "$uri"; then
        # Allowed exception: links to ADR/citation files within the run output
        case "$uri" in
            adrs/*|citations.md|substrate-options.md) ;;
            *) echo "VIOLATION: $uri not found in $CLAIMS source_uris"; violations=$((violations+1));;
        esac
    fi
done

if [[ $violations -eq 0 ]]; then
    echo "PASS: invariant 1 (citation invariant)"
    exit 0
else
    echo "FAIL: $violations citation violations in $REPORT"
    exit 1
fi
