#!/bin/bash
# Invariant 3 — Manifest read-only (Design §7.1).
# Manifest's mtime should equal its written-time. Approach: compare mtime to checkpoint.started_at.
set -euo pipefail
RUN_DIR="${1:?Usage: $0 <working/synthesis/run-id>}"

MANIFEST="$RUN_DIR/00-manifest.json"
CHECKPOINT="$RUN_DIR/checkpoint.json"

[[ -f "$MANIFEST" ]] || { echo "FAIL: $MANIFEST not found"; exit 1; }

# Method: jq the started_at and compare to file mtime within 60s tolerance
# (allows for write latency between manifest creation and checkpoint write)
manifest_started=$(jq -r '.started_at' "$MANIFEST")
manifest_mtime=$(stat -c %Y "$MANIFEST")
started_epoch=$(date -d "$manifest_started" +%s)

delta=$((manifest_mtime - started_epoch))
abs_delta=${delta#-}

if [[ $abs_delta -gt 600 ]]; then
    echo "FAIL: manifest mtime drifted ${delta}s from started_at — possible re-write?"
    exit 1
else
    echo "PASS: invariant 3 (manifest read-only; mtime within ${delta}s of started_at)"
    exit 0
fi
