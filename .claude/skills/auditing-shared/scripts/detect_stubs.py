#!/usr/bin/env python3
"""Detect stub patterns in implementation and test files.

Per AC-FR-2-d + Q-CC-2 (path-aware patterns) + D-2d (centralized stub
detection). Maintains TWO pattern sets:

- Implementation files: pass\\s*$ in non-trivial function bodies,
  raise NotImplementedError, TODO, FIXME, // stub, # stub
- Test files (paths matching tests/, test_*, *_test.*, *.test.*, *.spec.*):
  assert True\\s*$ as sole assertion, assert False\\s*$, # TODO: test,
  // TODO: assert, completely-empty test function bodies (after docstring),
  test names containing _stub or _placeholder

Findings carry severity: blocker for impl-file stubs and severity: major
for test-file stubs (per Q-CC-2 rationale).

False-positive suppression: a legitimate `pass` inside a trivially-empty
exception handler (e.g., `except KeyError: pass`) inside an otherwise
non-trivial function body is NOT flagged. The `pass`-as-sole-function-body
case IS flagged.
"""
import argparse
import ast
import json
import re
import sys
from pathlib import Path


TEST_PATH_RE = re.compile(
    r"(?:^|/)(?:tests?/|test_|.*_test\.|.*\.test\.|.*\.spec\.)",
    re.IGNORECASE,
)

IMPL_TEXT_PATTERNS = [
    (re.compile(r"raise\s+NotImplementedError"), "raise NotImplementedError"),
    (re.compile(r"#\s*stub\b", re.IGNORECASE), "# stub"),
    (re.compile(r"//\s*stub\b", re.IGNORECASE), "// stub"),
    (re.compile(r"\bTODO\b"), "TODO marker"),
    (re.compile(r"\bFIXME\b"), "FIXME marker"),
]

TEST_TEXT_PATTERNS = [
    (re.compile(r"#\s*TODO:\s*test", re.IGNORECASE), "# TODO: test"),
    (re.compile(r"//\s*TODO:\s*assert", re.IGNORECASE), "// TODO: assert"),
    (re.compile(r"^\s*assert\s+True\s*$"), "assert True (sole assertion)"),
    (re.compile(r"^\s*assert\s+False\s*$"), "assert False"),
]


def is_test_path(path: Path) -> bool:
    return bool(TEST_PATH_RE.search(str(path)))


def _function_is_stub_body(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """A function whose body is ONLY pass / ellipsis / docstring is a stub."""
    body = list(node.body)
    # Skip leading docstring.
    if (
        body
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    ):
        body = body[1:]
    if not body:
        return True
    if len(body) == 1:
        stmt = body[0]
        if isinstance(stmt, ast.Pass):
            return True
        if (
            isinstance(stmt, ast.Expr)
            and isinstance(stmt.value, ast.Constant)
            and stmt.value.value is Ellipsis
        ):
            return True
        if isinstance(stmt, ast.Raise):
            exc = stmt.exc
            if isinstance(exc, ast.Call) and isinstance(exc.func, ast.Name):
                if exc.func.id == "NotImplementedError":
                    return True
            elif isinstance(exc, ast.Name) and exc.id == "NotImplementedError":
                return True
    return False


def scan_python_ast_for_stubs(path: Path, text: str, is_test: bool) -> list[dict]:
    """Use AST to detect function-body stubs (more precise than regex)."""
    findings: list[dict] = []
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError:
        return findings

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not _function_is_stub_body(node):
            continue
        name = node.name
        # Detect test-name stub markers.
        is_test_function = is_test and (
            name.startswith("test_")
            or "_stub" in name
            or "_placeholder" in name
        )
        sev = "major" if (is_test or is_test_function) else "blocker"
        findings.append(
            {
                "domain": "stub",
                "severity": sev,
                "source_activity": "stub-detection",
                "file_path": str(path),
                "message": (
                    f"function '{name}' has stub body "
                    f"(pass/.../docstring-only/NotImplementedError) at line {node.lineno}"
                ),
                "dispatch_hint": "n/a (escalates per D-2d)",
                "depth_level": "0",
                "line": node.lineno,
            }
        )

    # Test-specific: name contains _stub or _placeholder regardless of body.
    if is_test:
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if "_stub" in node.name or "_placeholder" in node.name:
                findings.append(
                    {
                        "domain": "stub",
                        "severity": "major",
                        "source_activity": "stub-detection",
                        "file_path": str(path),
                        "message": (
                            f"test function name '{node.name}' marks placeholder "
                            f"at line {node.lineno}"
                        ),
                        "dispatch_hint": "n/a (escalates per D-2d)",
                        "depth_level": "0",
                        "line": node.lineno,
                    }
                )
    return findings


def scan_text_patterns(path: Path, text: str, is_test: bool) -> list[dict]:
    """Regex-based pattern scan for stub markers, line-by-line."""
    findings: list[dict] = []
    patterns = TEST_TEXT_PATTERNS if is_test else IMPL_TEXT_PATTERNS
    sev = "major" if is_test else "blocker"
    for lineno, line in enumerate(text.splitlines(), start=1):
        # Skip the script's own docstring lines documenting patterns it itself
        # detects (heuristic: lines clearly within a triple-quoted string at
        # the file top — handled by skipping lines before the first non-string
        # statement). Simple version: skip if file is this very script.
        if path.name == "detect_stubs.py":
            continue
        for pat, label in patterns:
            if pat.search(line):
                findings.append(
                    {
                        "domain": "stub",
                        "severity": sev,
                        "source_activity": "stub-detection",
                        "file_path": str(path),
                        "message": f"{label} at line {lineno}",
                        "dispatch_hint": "n/a (escalates per D-2d)",
                        "depth_level": "0",
                        "line": lineno,
                        "match": pat.pattern,
                    }
                )
    return findings


def find_findings(path: Path) -> list[dict]:
    if not path.exists() or not path.is_file():
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    is_test = is_test_path(path)
    findings: list[dict] = []
    if path.suffix == ".py":
        findings.extend(scan_python_ast_for_stubs(path, text, is_test))
    findings.extend(scan_text_patterns(path, text, is_test))
    return findings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "paths",
        nargs="*",
        help="Files to scan. If omitted, read newline-separated paths from stdin.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths: list[Path]
    if args.paths:
        paths = [Path(p) for p in args.paths]
    else:
        paths = [Path(line.strip()) for line in sys.stdin if line.strip()]

    findings: list[dict] = []
    for p in paths:
        if p.is_dir():
            for sub in p.rglob("*"):
                if sub.is_file():
                    findings.extend(find_findings(sub))
            continue
        findings.extend(find_findings(p))

    sys.stdout.write(json.dumps({"findings": findings}, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
