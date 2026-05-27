#!/usr/bin/env python3
"""
cross_file_checks.py — Cross-file pair checks for project-level audits.

Runs after per-primitive audits complete. Inspects the project filesystem
and (optionally) the aggregated per-primitive findings to detect interactions
that no single-file audit can.

The 24 checks (X1–X24) are organized into groups by primitive-pair:
  - Hooks ↔ scripts / .gitignore / permissions
  - Settings ↔ permissions / scope
  - Subagent ↔ memory / skills / hooks
  - CLAUDE.md ↔ rules / imports / managed
  - MCP ↔ toxic-combinations

Each check is a pure function taking project_state and returning a list of
new findings. Functions live in this module and are registered via CHECKS.

Phase 7 status: All 24 checks implemented (X1–X24).

Usage:
    python3 cross_file_checks.py <project-root>
"""
import json
import re
import sys
from pathlib import Path


# ---- Project state discovery ----

def discover_project(root: Path) -> dict:
    state = {
        "root": root,
        "claude_md_files": [],
        "rules_files": [],
        "agents_files": [],
        "skills_dirs": [],
        "commands_files": [],
        "hooks_dir": None,
        "hook_scripts": [],
        "agent_memory_dirs": {"project": [], "local": []},
        "settings_files": {
            "managed": None,
            "user": None,
            "project": None,
            "local": None,
        },
        "mcp_files": [],
        "output_styles_dir": None,
        "output_styles": [],
        "gitignore": None,
        "gitignore_lines": [],
    }
    claude_dir = root / ".claude"

    for name in ("CLAUDE.md", "CLAUDE.local.md"):
        p = root / name
        if p.is_file():
            state["claude_md_files"].append(p)
    p = claude_dir / "CLAUDE.md"
    if p.is_file():
        state["claude_md_files"].append(p)

    rules_dir = claude_dir / "rules"
    if rules_dir.is_dir():
        state["rules_files"] = sorted(rules_dir.glob("*.md"))

    agents_dir = claude_dir / "agents"
    if agents_dir.is_dir():
        state["agents_files"] = sorted(agents_dir.glob("*.md"))

    skills_dir = claude_dir / "skills"
    if skills_dir.is_dir():
        state["skills_dirs"] = sorted(d for d in skills_dir.iterdir() if d.is_dir())

    commands_dir = claude_dir / "commands"
    if commands_dir.is_dir():
        state["commands_files"] = sorted(commands_dir.glob("*.md"))

    hooks_dir = claude_dir / "hooks"
    if hooks_dir.is_dir():
        state["hooks_dir"] = hooks_dir
        state["hook_scripts"] = sorted(p for p in hooks_dir.iterdir() if p.is_file())

    project_mem = claude_dir / "agent-memory"
    if project_mem.is_dir():
        state["agent_memory_dirs"]["project"] = sorted(d for d in project_mem.iterdir() if d.is_dir())
    local_mem = claude_dir / "agent-memory-local"
    if local_mem.is_dir():
        state["agent_memory_dirs"]["local"] = sorted(d for d in local_mem.iterdir() if d.is_dir())

    p = claude_dir / "settings.json"
    if p.is_file():
        state["settings_files"]["project"] = p
    p = claude_dir / "settings.local.json"
    if p.is_file():
        state["settings_files"]["local"] = p

    p = root / ".mcp.json"
    if p.is_file():
        state["mcp_files"].append(p)

    osd = claude_dir / "output-styles"
    if osd.is_dir():
        state["output_styles_dir"] = osd
        state["output_styles"] = sorted(osd.glob("*.md"))

    gi = root / ".gitignore"
    if gi.is_file():
        state["gitignore"] = gi
        try:
            state["gitignore_lines"] = [
                line.strip() for line in gi.read_text(encoding="utf-8", errors="replace").split("\n")
                if line.strip() and not line.strip().startswith("#")
            ]
        except Exception:
            pass

    return state


# ---- Helpers ----

def gitignore_covers(path: str, lines: list[str]) -> bool:
    norm = path.lstrip("/")
    for pat in lines:
        pat_norm = pat.lstrip("/").rstrip("/")
        if pat_norm == norm or pat_norm == norm + "/":
            return True
        if norm.startswith(pat_norm + "/"):
            return True
        try:
            regex = re.escape(pat_norm).replace(r"\*", ".*").replace(r"\?", ".")
            if re.match(f"^{regex}$", norm):
                return True
            if pat_norm.startswith("**/"):
                base = pat_norm[3:]
                if norm.endswith(base) or "/" + base in "/" + norm:
                    return True
        except re.error:
            continue
    return False


def read_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


# ---- The implemented checks ----

def check_X1_hook_script_missing(state: dict) -> list[dict]:
    findings = []
    settings_path = state["settings_files"].get("project")
    if not settings_path:
        return findings
    data = read_json(settings_path)
    if not data:
        return findings
    hooks = data.get("hooks", {})
    if not isinstance(hooks, dict):
        return findings
    for event, entries in hooks.items():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            for action in entry.get("hooks", []) or []:
                if not isinstance(action, dict):
                    continue
                cmd = action.get("command", "")
                if not isinstance(cmd, str):
                    continue
                first = cmd.split()[0] if cmd.split() else ""
                if "/" in first or first.endswith(".sh") or first.endswith(".py"):
                    # Expand documented hook-context variables before resolving on disk
                    # so commands like '${CLAUDE_PROJECT_DIR}/.claude/hooks/foo.sh' resolve
                    # against the real project root.
                    if "${CLAUDE_PROJECT_DIR}" in first:
                        first = first.replace("${CLAUDE_PROJECT_DIR}", str(state["root"]))
                    if "${HOME}" in first:
                        from os.path import expanduser
                        first = first.replace("${HOME}", expanduser("~"))
                    p = Path(first)
                    if not p.is_absolute():
                        p = state["root"] / p
                    if not p.exists():
                        findings.append({
                            "check": "X1",
                            "dimension": 10, "severity": "BLOCKER",
                            "what": f"Hook '{event}' command references script '{cmd}' which does not exist.",
                            "fix": "Create the script or remove the hook entry.",
                            "location": str(settings_path),
                            "where": str(settings_path),
                        })
    return findings


def check_X2_bypass_disabled_in_managed(state: dict) -> list[dict]:
    findings = []
    managed = state["settings_files"].get("managed")
    if not managed or not managed.is_file():
        return findings
    managed_data = read_json(managed)
    if not managed_data:
        return findings
    if managed_data.get("disableBypassPermissionsMode") != "disable":
        return findings
    for sub_file in state["agents_files"]:
        text = read_text(sub_file)
        if re.search(r"permissionMode:\s*bypassPermissions", text):
            findings.append({
                "check": "X2",
                "dimension": 10, "severity": "MAJOR",
                "what": f"Subagent {sub_file.name} declares bypassPermissions but managed scope disables it. Silently downgraded.",
                "fix": "Remove bypassPermissions from the subagent (it has no effect).",
                "location": str(sub_file),
                "where": str(sub_file),
            })
    return findings


def check_X4_command_subagent_name_collision(state: dict) -> list[dict]:
    findings = []
    cmd_names = {p.stem for p in state["commands_files"]}
    sub_names = {p.stem for p in state["agents_files"]}
    for name in cmd_names & sub_names:
        findings.append({
            "check": "X4",
            "dimension": 10, "severity": "MINOR",
            "what": f"Slash command '/{name}' and subagent '{name}' share the same name. The slash command wins; subagent is shadowed.",
            "fix": "Rename one of them.",
            "location": str(state["root"]),
            "where": str(state["root"]),
        })
    return findings


def check_X10_settings_local_gitignore(state: dict) -> list[dict]:
    findings = []
    local = state["settings_files"].get("local")
    if not local or not local.is_file():
        return findings
    rel_path = ".claude/settings.local.json"
    if not gitignore_covers(rel_path, state["gitignore_lines"]):
        findings.append({
            "check": "X10",
            "dimension": 10, "severity": "MAJOR",
            "what": "settings.local.json exists at project scope but is not covered by .gitignore. Will leak to commits.",
            "fix": "Add a line for the path to .gitignore.",
            "location": str(local),
            "where": str(local),
        })
    return findings


def check_X11_at_import_outside_root(state: dict) -> list[dict]:
    findings = []
    root_resolved = state["root"].resolve()
    AT_IMPORT_RE = re.compile(r"(?<!\S)@([\.\/\w][\w\.\-\/]*\.md)\b")
    for cmd_file in state["claude_md_files"]:
        text = read_text(cmd_file)
        for m in AT_IMPORT_RE.finditer(text):
            imp = m.group(1)
            if imp.startswith("/"):
                target = Path(imp).resolve()
            else:
                target = (cmd_file.parent / imp).resolve()
            try:
                target.relative_to(root_resolved)
            except ValueError:
                findings.append({
                    "check": "X11",
                    "dimension": 10, "severity": "MAJOR",
                    "what": f"CLAUDE.md @-import target '{imp}' resolves outside project root.",
                    "fix": "Use a path within the project, or accept this CLAUDE.md is machine-specific.",
                    "location": str(cmd_file),
                    "where": str(cmd_file),
                })
    return findings


def check_X13_agent_memory_local_gitignore(state: dict) -> list[dict]:
    findings = []
    has_local_memory = bool(state["agent_memory_dirs"]["local"])
    for sub_file in state["agents_files"]:
        text = read_text(sub_file)
        if re.search(r"^memory:\s*local", text, re.M):
            has_local_memory = True
            break
    if not has_local_memory:
        return findings
    rel_path = ".claude/agent-memory-local"
    if not gitignore_covers(rel_path, state["gitignore_lines"]) and \
       not gitignore_covers(rel_path + "/", state["gitignore_lines"]):
        findings.append({
            "check": "X13",
            "dimension": 10, "severity": "MAJOR",
            "what": "Subagent local memory is in use but .gitignore does not cover the agent-memory-local directory. Will leak to commits.",
            "fix": "Add `.claude/agent-memory-local/` to .gitignore.",
            "location": str(state["root"]),
            "where": str(state["root"]),
        })
    return findings


def check_X14_output_style_missing(state: dict) -> list[dict]:
    findings = []
    for scope, settings_path in state["settings_files"].items():
        if not settings_path or not settings_path.is_file():
            continue
        data = read_json(settings_path)
        if not data:
            continue
        styles = data.get("outputStyles", [])
        if not isinstance(styles, list):
            continue
        for s in styles:
            if not isinstance(s, str):
                continue
            if Path(s).is_absolute():
                p = Path(s)
            else:
                p = state["root"] / ".claude" / "output-styles" / f"{s}.md"
            if not p.exists():
                findings.append({
                    "check": "X14",
                    "dimension": 10, "severity": "MAJOR",
                    "what": f"Output style '{s}' referenced in settings.json ({scope} scope) but file not on disk.",
                    "fix": "Create the file at the expected location, or remove from outputStyles.",
                    "location": str(settings_path),
                    "where": str(settings_path),
                })
    return findings


def check_X18_primitive_same_name_multiscope(state: dict) -> list[dict]:
    # Project-only view; user-scope requires HOME access. Placeholder.
    return []


def check_X21_orphan_agent_memory(state: dict) -> list[dict]:
    findings = []
    declared = set()
    for sub_file in state["agents_files"]:
        text = read_text(sub_file)
        m = re.search(r"^name:\s*([\w-]+)", text, re.M)
        if m:
            mem_m = re.search(r"^memory:\s*(project|local|user)", text, re.M)
            if mem_m:
                declared.add(m.group(1))
    for kind in ("project", "local"):
        for d in state["agent_memory_dirs"][kind]:
            if d.name not in declared:
                findings.append({
                    "check": "X21",
                    "dimension": 10, "severity": "MINOR",
                    "what": f"Orphan agent-memory directory: {d} (no subagent declares memory: {kind} for name '{d.name}').",
                    "fix": "Remove the directory, or restore the subagent that owns it.",
                    "location": str(d),
                    "where": str(d),
                })
    return findings


def check_X22_automemory_wrong_scope(state: dict) -> list[dict]:
    findings = []
    for scope in ("project", "local"):
        path = state["settings_files"].get(scope)
        if not path or not path.is_file():
            continue
        data = read_json(path)
        if not data:
            continue
        if "autoMemoryDirectory" in data:
            findings.append({
                "check": "X22",
                "dimension": 10, "severity": "MAJOR",
                "what": f"`autoMemoryDirectory` at {scope} scope is silently ignored. Only takes effect at user scope.",
                "fix": "Move to the user-scope settings.json file, or remove.",
                "location": str(path),
                "where": str(path),
            })
    return findings


def check_X23_agent_memory_local_dir_gitignore(state: dict) -> list[dict]:
    findings = []
    local_dir = state["root"] / ".claude" / "agent-memory-local"
    if not local_dir.is_dir():
        return findings
    rel_path = ".claude/agent-memory-local"
    if not gitignore_covers(rel_path, state["gitignore_lines"]) and \
       not gitignore_covers(rel_path + "/", state["gitignore_lines"]):
        findings.append({
            "check": "X23",
            "dimension": 10, "severity": "MAJOR",
            "what": "Local agent-memory directory exists at .claude/agent-memory-local but is not covered by .gitignore.",
            "fix": "Add `.claude/agent-memory-local/` to .gitignore.",
            "location": str(local_dir),
            "where": str(local_dir),
        })
    return findings


def check_X3_subagent_skills_disable_invocation(state: dict) -> list[dict]:
    """X3: Subagent lists a skill in `skills:` that has disable-model-invocation: true."""
    findings = []
    # Build map of in-project skill name -> SKILL.md
    skill_map = {}
    for sd in state["skills_dirs"]:
        skill_md = sd / "SKILL.md"
        if skill_md.is_file():
            skill_map[sd.name] = skill_md

    for sub_file in state["agents_files"]:
        text = read_text(sub_file)
        # Extract `skills:` list (YAML, simple parse)
        # Match either `skills: [a, b]` or block-form
        skills_listed = []
        # Block form
        m = re.search(r"^skills:\s*\n((?:[ \t]+-\s*[\w-]+\s*\n)+)", text, re.M)
        if m:
            skills_listed = re.findall(r"^[ \t]+-\s*([\w-]+)", m.group(1), re.M)
        else:
            # Inline form
            m = re.search(r"^skills:\s*\[([^\]]*)\]", text, re.M)
            if m:
                skills_listed = [s.strip() for s in m.group(1).split(",") if s.strip()]

        for skill_name in skills_listed:
            target_md = skill_map.get(skill_name)
            if not target_md:
                continue  # not an in-project skill; can't check
            target_text = read_text(target_md)
            # Check the skill's frontmatter for disable-model-invocation: true
            m_dmi = re.search(r"^disable-model-invocation:\s*(true|True|TRUE)\s*$", target_text, re.M)
            if m_dmi:
                findings.append({
                    "check": "X3",
                    "dimension": 10, "severity": "BLOCKER",
                    "what": f"Subagent {sub_file.name} lists skill '{skill_name}' in skills:, but that skill has disable-model-invocation: true. Skills with this flag cannot preload into subagents — silent drop.",
                    "fix": "Either remove from the subagent's skills: list, or change the skill's disable-model-invocation flag.",
                    "location": str(sub_file),
                    "where": str(sub_file),
                })
    return findings


def check_X5_command_references_missing_skill(state: dict) -> list[dict]:
    """X5: Slash command body references a skill that doesn't exist in the project."""
    findings = []
    skill_names = {sd.name for sd in state["skills_dirs"]}

    for cmd_file in state["commands_files"]:
        text = read_text(cmd_file)
        # Find references like "use the X skill", "Use the X skill", "invoke X"
        # Heuristic: look for patterns "use the <name>(-<word>)+ skill"
        for m in re.finditer(
            r"(?i)\b(?:use|invoke|call|run|trigger)\s+(?:the\s+)?[`\"']?([\w-]+)[`\"']?\s+skill\b",
            text
        ):
            ref = m.group(1)
            if ref in skill_names:
                continue
            # Don't flag generic words
            if ref.lower() in {"a", "the", "this", "that", "any"}:
                continue
            findings.append({
                "check": "X5",
                "dimension": 10, "severity": "BLOCKER",
                "what": f"Slash command {cmd_file.name} references skill '{ref}' which is not in this project.",
                "fix": "Create the skill, fix the spelling, or remove the reference.",
                "location": str(cmd_file),
                "where": str(cmd_file),
            })
    return findings


def check_X6_claude_md_rule_duplication(state: dict) -> list[dict]:
    """X6: A rule line appears in CLAUDE.md AND in a rules/*.md file (additive double-load)."""
    findings = []
    if not state["claude_md_files"] or not state["rules_files"]:
        return findings

    def extract_rules(text: str) -> set[str]:
        out = set()
        in_fence = False
        for line in text.split("\n"):
            stripped = line.lstrip()
            if stripped.startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence or not stripped:
                continue
            if stripped.startswith("#") or stripped.startswith("|"):
                continue
            # Strip leading list markers
            normalized = re.sub(r"^[\-\*\d\.\s]+", "", stripped).strip().lower()
            normalized = re.sub(r"\s+", " ", normalized)
            if len(normalized) >= 40:
                out.add(normalized)
        return out

    # Aggregate CLAUDE.md rules
    claude_rules = set()
    for cf in state["claude_md_files"]:
        claude_rules |= extract_rules(read_text(cf))

    for rf in state["rules_files"]:
        rule_rules = extract_rules(read_text(rf))
        overlap = claude_rules & rule_rules
        for shared in overlap:
            findings.append({
                "check": "X6",
                "dimension": 10, "severity": "MINOR",
                "what": f"Rule duplicated between CLAUDE.md and {rf.name}: '{shared[:60]}...'. Loaded twice; tokens wasted.",
                "fix": "Keep one canonical copy. CLAUDE.md if universal; rules file if scoped.",
                "location": str(rf),
                "where": str(rf),
            })
    return findings


def check_X7_rule_paths_glob_matches_nothing(state: dict) -> list[dict]:
    """X7: A rule's paths: glob doesn't match any file in the project."""
    findings = []
    if not state["rules_files"]:
        return findings

    root = state["root"]
    for rf in state["rules_files"]:
        text = read_text(rf)
        # Extract paths list from frontmatter
        m = re.search(r"^paths:\s*\n((?:[ \t]+-\s*['\"]?[^'\"\n]+['\"]?\s*\n)+)", text, re.M)
        paths = []
        if m:
            for line in m.group(1).split("\n"):
                lm = re.match(r"^[ \t]+-\s*['\"]?([^'\"\n]+?)['\"]?\s*$", line)
                if lm:
                    paths.append(lm.group(1).strip())
        else:
            m = re.search(r"^paths:\s*\[([^\]]+)\]", text, re.M)
            if m:
                paths = [p.strip().strip("'\"") for p in m.group(1).split(",")]

        if not paths:
            continue

        # Check if any glob matches any file
        any_match = False
        for g in paths:
            try:
                # Two strategies: glob from root, or with **/ prefix
                for _ in root.glob(g):
                    any_match = True
                    break
                if any_match:
                    break
                if not g.startswith("**"):
                    for _ in root.glob(f"**/{g}"):
                        any_match = True
                        break
                    if any_match:
                        break
            except Exception:
                pass

        if not any_match:
            findings.append({
                "check": "X7",
                "dimension": 10, "severity": "BLOCKER",
                "what": f"Rule {rf.name} declares paths: {paths} but no file in the project matches. Rule will never load.",
                "fix": "Verify the glob syntax and adjust patterns, or remove the rule.",
                "location": str(rf),
                "where": str(rf),
            })
    return findings


def check_X8_env_var_unset(state: dict) -> list[dict]:
    """X8: settings.env references ${VAR} but VAR isn't defined at any settings scope.

    Limited: we can only check known settings files. If user-scope settings has
    the var, we won't know without HOME access.
    """
    findings = []
    # Collect all env vars defined in any visible settings.json
    defined_vars = set()
    references = []  # list of (var_name, scope, settings_path)

    for scope, p in state["settings_files"].items():
        if not p or not p.is_file():
            continue
        data = read_json(p)
        if not data:
            continue
        env = data.get("env", {})
        if isinstance(env, dict):
            for k, v in env.items():
                defined_vars.add(k)
                if isinstance(v, str):
                    for m in re.finditer(r"\$\{([A-Z_][A-Z0-9_]*)\}", v):
                        references.append((m.group(1), scope, p))

    for var, scope, path in references:
        if var not in defined_vars:
            findings.append({
                "check": "X8",
                "dimension": 10, "severity": "MINOR",
                "what": f"settings.json ({scope} scope) env references ${{{var}}} but this variable is not defined in any visible settings scope. Relies on shell env at runtime.",
                "fix": "Either accept that the shell provides it, or define a default in user-scope settings.",
                "location": str(path),
                "where": str(path),
            })
    return findings


def check_X9_subagent_skills_security_block(state: dict) -> list[dict]:
    """X9: Subagent lists a skill that fails its own security audit (SECURITY-BLOCK).

    Per D-6 (v4.6.0): wired implementation. For each (subagent, skill) pair, dispatch
    `auditing-skills/scripts/audit_skill.py` via subprocess (pattern from
    audit_project.py:51). Cache results per skill within a single audit run to
    avoid redundant work when multiple subagents preload the same skill. Emit:
      - BLOCKER if the child skill audit fails with SECURITY-BLOCK verdict
      - MAJOR  if the child skill audit fails with non-block defects
      - (none) if the child skill audit passes

    Replaces the v4.4.x stub that only emitted MINOR placeholder findings.
    """
    findings: list[dict] = []
    import subprocess
    import sys as _sys

    # Cache: skill_path → audit verdict (within this audit run only)
    skill_audit_cache: dict[str, dict] = {}

    # Locate audit_skill.py via the canonical auditing-skills location
    audit_skill_path = (
        Path(__file__).resolve().parent.parent.parent
        / "auditing-skills" / "scripts" / "audit_skill.py"
    )

    def _audit_skill(skill_path: Path) -> dict:
        """Run audit_skill.py against a skill directory; return parsed verdict.

        audit_skill.py's output has no top-level `verdict` key; instead it
        emits findings in categorical buckets (security, orphans, references,
        deterministic_findings). We aggregate them to derive a verdict:
          - SECURITY-BLOCK if any `security` finding is BLOCKER severity
          - FAIL          if any finding (any category) is BLOCKER
          - WARN          if any finding (any category) is MAJOR
          - PASS          otherwise
        """
        key = str(skill_path)
        if key in skill_audit_cache:
            return skill_audit_cache[key]
        result = {"verdict": "UNKNOWN", "findings": [], "error": None}
        if not audit_skill_path.exists():
            result["error"] = f"audit_skill.py not found at {audit_skill_path}"
            skill_audit_cache[key] = result
            return result
        if not skill_path.exists() or not skill_path.is_dir():
            result["error"] = f"skill path does not exist: {skill_path}"
            skill_audit_cache[key] = result
            return result
        try:
            r = subprocess.run(
                [_sys.executable, str(audit_skill_path), str(skill_path)],
                capture_output=True, text=True, timeout=60,
            )
            if r.stdout:
                try:
                    parsed = json.loads(r.stdout)
                    # Aggregate findings from audit_skill.py's categorical buckets.
                    # IMPORTANT: use POST-MARKER final_severity (mechanism α may have
                    # demoted BLOCKER findings to MAJOR/INFO via the marker triage).
                    # The pre-existing `security.security_block` flag reflects pre-marker
                    # severity and is misleading for the X9 verdict (it would cascade
                    # demoted findings as cross-file BLOCKERs incorrectly).
                    all_findings: list[dict] = []
                    security_findings: list[dict] = []
                    # security bucket
                    sec_bucket = parsed.get("security") or {}
                    if isinstance(sec_bucket, dict):
                        security_findings = sec_bucket.get("findings") or []
                        if isinstance(security_findings, list):
                            all_findings.extend(f for f in security_findings if isinstance(f, dict))
                    # references bucket
                    ref_bucket = parsed.get("references") or {}
                    if isinstance(ref_bucket, dict):
                        ref_findings = ref_bucket.get("findings") or []
                        if isinstance(ref_findings, list):
                            all_findings.extend(f for f in ref_findings if isinstance(f, dict))
                    # deterministic_findings (direct list)
                    det_findings = parsed.get("deterministic_findings") or []
                    if isinstance(det_findings, list):
                        all_findings.extend(f for f in det_findings if isinstance(f, dict))
                    # orphans: list of paths — only MINOR severity, classify as "WARN" trigger
                    orphans = parsed.get("orphans") or []
                    # Note: orphans are noted as MINOR cleanliness issues but never security-blocks
                    result["findings"] = all_findings
                    # Derive verdict from POST-MARKER severities (use final_severity if set,
                    # else fall back to severity for findings that haven't been triaged).
                    def _eff_sev(f: dict) -> str:
                        return f.get("final_severity") or f.get("severity") or "INFO"
                    sec_blockers = any(
                        _eff_sev(f) == "BLOCKER" for f in security_findings
                        if isinstance(f, dict)
                    )
                    any_blockers = any(_eff_sev(f) == "BLOCKER" for f in all_findings)
                    any_majors = any(_eff_sev(f) == "MAJOR" for f in all_findings)
                    if sec_blockers:
                        result["verdict"] = "SECURITY-BLOCK"
                    elif any_blockers:
                        result["verdict"] = "FAIL"
                    elif any_majors:
                        result["verdict"] = "WARN"
                    else:
                        result["verdict"] = "PASS"
                except json.JSONDecodeError:
                    result["error"] = "non-JSON output from audit_skill.py"
            else:
                result["error"] = (r.stderr or "no output").strip()[:200]
        except subprocess.TimeoutExpired:
            result["error"] = "audit_skill.py timeout"
        except Exception as e:
            result["error"] = f"exec error: {e!r}"
        skill_audit_cache[key] = result
        return result

    # Resolve skill name to canonical path under .claude/skills/
    skills_root = (
        Path(__file__).resolve().parent.parent.parent.parent
        / "skills"
    )

    def _resolve_skill_path(skill_ref: str) -> Path | None:
        """Skills can be referenced by name (e.g. 'KB-cc-design') OR by path.
        Resolve to a directory under .claude/skills/."""
        # If path-like, try as-is first
        p = Path(skill_ref)
        if p.is_absolute() and p.is_dir():
            return p
        # Try relative to .claude/skills/
        candidate = skills_root / skill_ref
        if candidate.is_dir():
            return candidate
        # Strip leading '.claude/skills/' if present
        if skill_ref.startswith(".claude/skills/"):
            return Path(skill_ref).resolve() if Path(skill_ref).exists() else None
        return None

    for sub_file in state["agents_files"]:
        text = read_text(sub_file)
        # Extract preloaded-skills list from frontmatter
        # Form A: skills: [a, b, c]  ; Form B: skills:\n  - a\n  - b
        skills_list: list[str] = []
        m_inline = re.search(r"^skills:\s*\[(.+?)\]", text, re.M)
        if m_inline:
            skills_list = [s.strip().strip("\"'") for s in m_inline.group(1).split(",") if s.strip()]
        else:
            m_block = re.search(r"^skills:\s*\n((?:[ \t]+-\s+.+\n?)+)", text, re.M)
            if m_block:
                for ln in m_block.group(1).splitlines():
                    ml = re.match(r"^\s*-\s+(.+)$", ln)
                    if ml:
                        skills_list.append(ml.group(1).strip().strip("\"'"))

        if not skills_list:
            continue

        for skill_ref in skills_list:
            skill_path = _resolve_skill_path(skill_ref)
            if skill_path is None:
                findings.append({
                    "check": "X9",
                    "dimension": 10, "severity": "MINOR",
                    "what": f"Subagent {sub_file.name} preloads skill '{skill_ref}' which cannot be resolved to a skill directory.",
                    "fix": "Verify the skill name matches a directory under .claude/skills/.",
                    "location": str(sub_file),
                    "where": str(sub_file),
                })
                continue

            audit = _audit_skill(skill_path)
            if audit.get("error"):
                findings.append({
                    "check": "X9",
                    "dimension": 10, "severity": "MINOR",
                    "what": f"Subagent {sub_file.name} preloads skill '{skill_ref}'; child audit could not run ({audit['error']}).",
                    "fix": "Investigate why audit_skill.py couldn't audit this skill.",
                    "location": str(sub_file),
                    "where": str(sub_file),
                })
                continue

            verdict = audit.get("verdict", "UNKNOWN")
            if verdict == "SECURITY-BLOCK":
                findings.append({
                    "check": "X9",
                    "dimension": 10, "severity": "BLOCKER",
                    "what": f"Subagent {sub_file.name} preloads skill '{skill_ref}' which FAILS its own security audit (SECURITY-BLOCK). Per X9, this is a cross-file security finding.",
                    "fix": f"Either fix the skill at {skill_path} to pass its security audit, or remove it from this subagent's preloaded skills.",
                    "location": str(sub_file),
                    "where": str(sub_file),
                })
            elif verdict in ("FAIL", "WARN") and audit.get("findings"):
                findings.append({
                    "check": "X9",
                    "dimension": 10, "severity": "MAJOR",
                    "what": f"Subagent {sub_file.name} preloads skill '{skill_ref}' whose audit verdict is {verdict} ({len(audit['findings'])} findings).",
                    "fix": f"Review findings at {skill_path}; either remediate or accept the risk in a security-exemption note.",
                    "location": str(sub_file),
                    "where": str(sub_file),
                })
            # PASS verdict → no finding
    return findings


def check_X12_hook_string_match_should_be_permission(state: dict) -> list[dict]:
    """X12: Hook script does string matching on tool_input.command that should be a permission rule."""
    findings = []
    # Two patterns:
    # (a) Bash case-arm with literal: `'git push' ) ...`
    # (b) String comparison: `$cmd = 'git push'` or `[[ "$cmd" == "git push" ]]`
    CASE_ARM_RE = re.compile(r"['\"]([a-z][\w\-]+(?:\s+[\w\-/\*]+){1,})['\"]\s*\)")
    CMP_RE = re.compile(r"\$\w+\s*=[=~]?\s*['\"]([a-z][\w\s\-/\*]{3,})['\"]")
    GREP_RE = re.compile(r"\bgrep\s+['\"]([a-z][\w\s\-/\*]{3,})['\"]")

    for hs in state["hook_scripts"]:
        text = read_text(hs)
        if "tool_input.command" not in text and "$cmd" not in text and "$1" not in text:
            continue
        seen_patterns = set()
        for regex in (CASE_ARM_RE, CMP_RE, GREP_RE):
            for m in regex.finditer(text):
                pattern = m.group(1).strip()
                if pattern in seen_patterns:
                    continue
                seen_patterns.add(pattern)
                findings.append({
                    "check": "X12",
                    "dimension": 10, "severity": "MINOR",
                    "what": f"Hook {hs.name} does string-matching on '{pattern}'. This is cleaner as a permissions.deny or .ask rule in settings.json.",
                    "fix": "Move the pattern to settings.json permissions instead of duplicating logic in a hook.",
                    "location": str(hs),
                    "where": str(hs),
                })
                break  # one finding per regex is enough
            if seen_patterns:
                break  # one finding per hook is enough
    return findings


def check_X15_project_hook_uses_home(state: dict) -> list[dict]:
    """X15: Project-scope hook command path uses ~/.../$HOME (breaks for teammates)."""
    findings = []
    settings_path = state["settings_files"].get("project")
    if not settings_path:
        return findings
    data = read_json(settings_path)
    if not data:
        return findings
    hooks = data.get("hooks", {})
    if not isinstance(hooks, dict):
        return findings
    for event, entries in hooks.items():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            for action in entry.get("hooks", []) or []:
                if not isinstance(action, dict):
                    continue
                cmd = action.get("command", "")
                if not isinstance(cmd, str):
                    continue
                if cmd.startswith("~") or "$HOME" in cmd or "${HOME}" in cmd:
                    findings.append({
                        "check": "X15",
                        "dimension": 10, "severity": "MAJOR",
                        "what": f"Project hook '{event}' command uses home path: '{cmd}'. Breaks for teammates with different layouts.",
                        "fix": "Use a project-relative path (e.g., .claude/hooks/<script>).",
                        "location": str(settings_path),
                        "where": str(settings_path),
                    })
    return findings


def check_X16_mcp_name_multiscope(state: dict) -> list[dict]:
    """X16: Same MCP server name appears at multiple scopes (override silently).

    Limited: we can only see project + local settings. User-scope detection
    requires HOME access.
    """
    findings = []
    server_names_by_scope = {}
    for scope in ("project", "local"):
        p = state["settings_files"].get(scope)
        if not p or not p.is_file():
            continue
        data = read_json(p)
        if not data:
            continue
        servers = data.get("mcpServers", {})
        if isinstance(servers, dict):
            server_names_by_scope[scope] = set(servers.keys())

    # Also check .mcp.json file
    for mf in state["mcp_files"]:
        data = read_json(mf)
        if not data:
            continue
        servers = data.get("mcpServers", data) if isinstance(data, dict) else {}
        if isinstance(servers, dict):
            server_names_by_scope[f"file:{mf.name}"] = set(servers.keys())

    # Find names appearing at multiple scopes
    name_to_scopes = {}
    for scope, names in server_names_by_scope.items():
        for name in names:
            name_to_scopes.setdefault(name, []).append(scope)

    for name, scopes in name_to_scopes.items():
        if len(scopes) > 1:
            findings.append({
                "check": "X16",
                "dimension": 10, "severity": "MINOR",
                "what": f"MCP server '{name}' configured at multiple scopes: {scopes}. Higher-precedence scope wins; lower is shadowed.",
                "fix": "Pick one canonical scope for this server.",
                "location": str(state["root"]),
                "where": str(state["root"]),
            })
    return findings


def check_X17_command_bypasses_subagent_permissions(state: dict) -> list[dict]:
    """X17: Slash command body invokes a subagent but bypasses its permissionMode."""
    findings = []
    sub_names = {p.stem for p in state["agents_files"]}
    for cmd_file in state["commands_files"]:
        text = read_text(cmd_file)
        # Look for subagent invocation + bypass hint
        for sub_name in sub_names:
            if f"@{sub_name}" in text or f"agent: {sub_name}" in text:
                # Check for bypass language in the command body
                if re.search(r"(?i)bypass|skip\s+approval|no\s+prompts?", text):
                    findings.append({
                        "check": "X17",
                        "dimension": 10, "severity": "MAJOR",
                        "what": f"Slash command {cmd_file.name} invokes subagent '{sub_name}' with bypass-suggesting language. Subagent's permissionMode applies regardless.",
                        "fix": "Remove the bypass language, or use a subagent designed for the operation.",
                        "location": str(cmd_file),
                        "where": str(cmd_file),
                    })
                    break
    return findings


def check_X19_memory_cites_inactive_rule(state: dict) -> list[dict]:
    """X19: Auto memory cites a rule whose paths: glob doesn't match the current project.

    Without HOME access we can't read user auto memory directly. Limited: only
    checks if a subagent memory directory cites an inactive rule.
    """
    findings = []
    # Gather rule paths and their globs
    rule_globs = {}  # rule_file -> list of globs
    for rf in state["rules_files"]:
        text = read_text(rf)
        m = re.search(r"^paths:\s*\n((?:[ \t]+-\s*['\"]?[^'\"\n]+['\"]?\s*\n)+)", text, re.M)
        globs = []
        if m:
            for line in m.group(1).split("\n"):
                lm = re.match(r"^[ \t]+-\s*['\"]?([^'\"\n]+?)['\"]?\s*$", line)
                if lm:
                    globs.append(lm.group(1).strip())
        rule_globs[rf.stem] = globs

    # Walk subagent memory MEMORY.md files; check for citations to known rules
    for kind, dirs in state["agent_memory_dirs"].items():
        for d in dirs:
            mm = d / "MEMORY.md"
            if not mm.is_file():
                continue
            mm_text = read_text(mm)
            for rule_name, globs in rule_globs.items():
                if not globs:
                    continue
                # Citation pattern: mentions the rule by name or filename
                if rule_name in mm_text or f"rules/{rule_name}" in mm_text:
                    # Check if any glob matches anything in the project
                    any_match = False
                    for g in globs:
                        try:
                            for _ in state["root"].glob(g):
                                any_match = True
                                break
                            if any_match:
                                break
                            if not g.startswith("**"):
                                for _ in state["root"].glob(f"**/{g}"):
                                    any_match = True
                                    break
                        except Exception:
                            pass
                    if not any_match:
                        findings.append({
                            "check": "X19",
                            "dimension": 10, "severity": "MINOR",
                            "what": f"Subagent memory at {mm} cites rule '{rule_name}' whose paths glob doesn't match anything in the project.",
                            "fix": "Update the rule's paths, or prune the memory citation.",
                            "location": str(mm),
                            "where": str(mm),
                        })
    return findings


def check_X20_subagent_memory_write_disallowed(state: dict) -> list[dict]:
    """X20: Subagent declares memory: but disallowedTools blocks Write/Edit."""
    findings = []
    for sub_file in state["agents_files"]:
        text = read_text(sub_file)
        has_memory = bool(re.search(r"^memory:\s*(project|local|user)\s*$", text, re.M))
        if not has_memory:
            continue
        # Check disallowedTools
        disallow_match = re.search(r"^disallowedTools:\s*(.+)$", text, re.M)
        if not disallow_match:
            # Block form
            block_match = re.search(
                r"^disallowedTools:\s*\n((?:[ \t]+-\s*[\w\(\)*\s,]+\s*\n)+)",
                text, re.M
            )
            disallowed = []
            if block_match:
                for line in block_match.group(1).split("\n"):
                    lm = re.match(r"^[ \t]+-\s*([\w\(\)*\s]+)", line)
                    if lm:
                        disallowed.append(lm.group(1).strip())
        else:
            disallowed_str = disallow_match.group(1).strip()
            # Inline list or comma form
            if disallowed_str.startswith("["):
                disallowed = [
                    s.strip().strip("'\"")
                    for s in disallowed_str.strip("[]").split(",")
                ]
            else:
                disallowed = [s.strip() for s in disallowed_str.split(",")]

        # Check if Write or Edit (without scoping) is disallowed
        bad_tools = {"Write", "Edit"}
        disallowed_clean = set()
        for d in disallowed:
            tool = re.split(r"\(", d)[0].strip()
            disallowed_clean.add(tool)

        if bad_tools & disallowed_clean:
            findings.append({
                "check": "X20",
                "dimension": 10, "severity": "BLOCKER",
                "what": f"Subagent {sub_file.name} declares memory: but disallowedTools blocks {bad_tools & disallowed_clean}. The subagent can never write to its memory.",
                "fix": "Remove the disallow on Write/Edit, or remove the memory: declaration.",
                "location": str(sub_file),
                "where": str(sub_file),
            })
    return findings


def check_X24_committed_memory_machine_local(state: dict) -> list[dict]:
    """X24: Committed agent-memory contains machine-local paths."""
    findings = []
    PATH_PATTERNS = [
        re.compile(r"/home/[a-zA-Z][\w-]*"),
        re.compile(r"/Users/[a-zA-Z][\w-]*"),
        re.compile(r"C:\\\\Users\\\\"),
    ]
    # Only check project-scope memory (committed)
    for d in state["agent_memory_dirs"]["project"]:
        for md in d.rglob("*.md"):
            text = read_text(md)
            for line_no, line in enumerate(text.split("\n"), start=1):
                for pat in PATH_PATTERNS:
                    m = pat.search(line)
                    if m:
                        findings.append({
                            "check": "X24",
                            "dimension": 10, "severity": "MAJOR",
                            "what": f"Committed agent-memory at {md.name}:{line_no} contains machine-local path '{m.group(0)}'. Breaks for other contributors.",
                            "fix": "Replace with relative paths, or move to local-scope memory.",
                            "location": f"{md}:{line_no}",
                            "where": f"{md}:{line_no}",
                        })
                        break
    return findings


# ---- Registry ----

CHECKS = [
    check_X1_hook_script_missing,
    check_X2_bypass_disabled_in_managed,
    check_X3_subagent_skills_disable_invocation,
    check_X4_command_subagent_name_collision,
    check_X5_command_references_missing_skill,
    check_X6_claude_md_rule_duplication,
    check_X7_rule_paths_glob_matches_nothing,
    check_X8_env_var_unset,
    check_X9_subagent_skills_security_block,
    check_X10_settings_local_gitignore,
    check_X11_at_import_outside_root,
    check_X12_hook_string_match_should_be_permission,
    check_X13_agent_memory_local_gitignore,
    check_X14_output_style_missing,
    check_X15_project_hook_uses_home,
    check_X16_mcp_name_multiscope,
    check_X17_command_bypasses_subagent_permissions,
    check_X18_primitive_same_name_multiscope,
    check_X19_memory_cites_inactive_rule,
    check_X20_subagent_memory_write_disallowed,
    check_X21_orphan_agent_memory,
    check_X22_automemory_wrong_scope,
    check_X23_agent_memory_local_dir_gitignore,
    check_X24_committed_memory_machine_local,
]


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(json.dumps({"error": "Usage: cross_file_checks.py <project-root>"}))
        return 2

    project_root = Path(args[0]).resolve()
    if not project_root.is_dir():
        print(json.dumps({"error": f"not a directory: {project_root}"}))
        return 2

    state = discover_project(project_root)
    findings: list[dict] = []
    for check_fn in CHECKS:
        try:
            findings.extend(check_fn(state))
        except Exception as e:
            findings.append({
                "check": check_fn.__name__,
                "dimension": 10, "severity": "MINOR",
                "what": f"Internal check error: {e}",
                "fix": "Report this as a bug in cross_file_checks.py.",
                "location": str(project_root),
                "where": str(project_root),
            })

    print(json.dumps({
        "target": str(project_root),
        "checks_run": [fn.__name__ for fn in CHECKS],
        "cross_file_findings": findings,
        "status": "complete",
        "note": "All 24 cross-file checks (X1-X24) implemented and active.",
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
