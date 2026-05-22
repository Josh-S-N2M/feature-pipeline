#!/bin/bash
# Invariant 7 — Recursion safety (Design §7.1).
# No file under output/synthesis-*/ appears in 01-claims*.json source_uri values.
set -euo pipefail
RUN_DIR="${1:?Usage: $0 <working/synthesis/run-id>}"

violations=0
files_to_check=$(find "$RUN_DIR" -type f \( -name "01-claims*.json" -o -path "*/per-source/01-claims-*.json" \) 2>/dev/null || true)

if [[ -z "$files_to_check" ]]; then
    echo "INFO: no 01-claims*.json files found in $RUN_DIR; vacuous PASS"
    exit 0
fi

while IFS= read -r f; do
    [[ -f "$f" ]] || continue
    bad=$(jq -r '.claims[].source_uri' "$f" 2>/dev/null | grep -E '^output/synthesis-' || true)
    if [[ -n "$bad" ]]; then
        echo "VIOLATION in $f:"
        echo "$bad"
        count=$(echo "$bad" | wc -l | tr -d ' ')
        violations=$((violations + count))
    fi
done <<< "$files_to_check"

if [[ $violations -eq 0 ]]; then
    echo "PASS: invariant 7 (recursion safety)"
    exit 0
else
    echo "FAIL: $violations recursion-safety violations"
    exit 1
fi
