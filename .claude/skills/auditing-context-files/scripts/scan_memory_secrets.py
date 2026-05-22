#!/usr/bin/env python3
"""DEPRECATED LOCAL COPY — shim that dispatches to the canonical implementation.

The canonical implementation lives at auditing-shared/scripts/scan_memory_secrets.py
per ADR-0031. This 3-line shim preserves call-site compatibility (callers invoke
`here / scan_memory_secrets.py` via subprocess; that resolves to this shim, which
in turn invokes the canonical and forwards stdout/exit code).

Per Plan v1.2.0 §P4.1 D-7 Option B (3-line shim fallback). Option A (delete +
caller update) was considered but rejected here because the shim costs less and
both callers' run_script() helpers use `here / script_name` resolution that would
require parallel updates.
"""
import os
import subprocess
import sys
from pathlib import Path

CANONICAL = Path(__file__).resolve().parent.parent.parent / "auditing-shared" / "scripts" / "scan_memory_secrets.py"
sys.exit(subprocess.run([sys.executable, str(CANONICAL)] + sys.argv[1:], env=os.environ).returncode)
