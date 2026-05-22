#!/usr/bin/env python3
"""DEPRECATED LOCAL COPY — shim that dispatches to the canonical implementation.

The canonical implementation lives at auditing-shared/scripts/pedagogical_marker_check.py
per ADR-0030 + ADR-0031. This 3-line shim preserves call-site compatibility for
the per-module callers (audit_skill.py, audit_subagent.py, triage_with_judge.py)
that historically expected a local pedagogical_marker_check.py.

Mechanism α (ADR-0030) is enforced ONLY in the canonical script. Calls through
this shim get full mechanism-α semantics: justification validation, marker
rejection on invalid/missing justification, surfacing of underlying findings.

Per Plan v1.2.0 §P4.1 D-7 Option B (3-line shim fallback).
"""
import os
import subprocess
import sys
from pathlib import Path

CANONICAL = Path(__file__).resolve().parent.parent.parent / "auditing-shared" / "scripts" / "pedagogical_marker_check.py"
sys.exit(subprocess.run([sys.executable, str(CANONICAL)] + sys.argv[1:], env=os.environ).returncode)
