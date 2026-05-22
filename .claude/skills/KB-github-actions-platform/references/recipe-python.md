# Recipes: Python

Patterns for Python projects on GitHub Actions. Covers uv, pip, ruff, mypy, pytest, version matrices, and PyPI publishing.

## Table of contents

- [Setup basics](#setup-basics)
- [Package manager: uv vs pip vs poetry](#package-manager-uv-vs-pip-vs-poetry)
- [Standard CI pipeline](#standard-ci-pipeline)
- [Linting: ruff](#linting-ruff)
- [Type checking: mypy, pyright](#type-checking-mypy-pyright)
- [Testing: pytest](#testing-pytest)
- [Version matrices](#version-matrices)
- [Publishing to PyPI](#publishing-to-pypi)

For a ready-to-use template, see `assets/templates/ci-python.yml` and `assets/templates/release-pypi.yml`.

## Setup basics

```yaml
- uses: actions/checkout@v6
- uses: actions/setup-python@v6
  with:
    python-version: '3.13'
    cache: pip          # or pipenv, poetry; auto-detects requirements*.txt or pyproject.toml
```

Python version policy:
- **3.10** — minimum reasonable for new code (3.9 reaches EOL October 2025).
- **3.11, 3.12, 3.13** — all current; pick based on dependencies and feature needs.
- For libraries: matrix on 3.10 through current.
- For applications: pin to one (the deployment target's version).

Use `python-version-file:` if the project has a `.python-version` (pyenv/uv convention):
```yaml
- uses: actions/setup-python@v6
  with: { python-version-file: '.python-version', cache: pip }
```

## Package manager: uv vs pip vs poetry

### uv (recommended for new projects)

[uv](https://docs.astral.sh/uv/) is a fast Python package and project manager from Astral. Replaces `pip`, `pip-tools`, `pipenv`, `pyenv`, and parts of `poetry` with one binary.

```yaml
- uses: actions/checkout@v6
- uses: astral-sh/setup-uv@SHA   # pin to current SHA
  with:
    enable-cache: true
- run: uv sync --all-extras --dev
- run: uv run pytest
```

`uv sync` reads `pyproject.toml` and `uv.lock` and creates a virtualenv at `.venv/`. `uv run <cmd>` executes inside the venv. Subsequent runs are fast thanks to uv's content-addressable cache.

Setup-uv handles caching automatically when `enable-cache: true`. No need for `actions/setup-python` if uv manages the Python install (it can download the requested interpreter).

```yaml
- uses: astral-sh/setup-uv@SHA
  with:
    enable-cache: true
    python-version: '3.13'   # uv installs this Python if not present
```

### pip + venv

```yaml
- uses: actions/checkout@v6
- uses: actions/setup-python@v6
  with: { python-version: '3.13', cache: pip }
- run: |
    python -m venv .venv
    . .venv/bin/activate
    pip install -e '.[dev]'
- run: |
    . .venv/bin/activate
    pytest
```

Or without an explicit venv (system-Python, fine for CI):
```yaml
- run: pip install -e '.[dev]'
- run: pytest
```

### Poetry

```yaml
- uses: actions/checkout@v6
- uses: actions/setup-python@v6
  with: { python-version: '3.13' }
- name: Install Poetry
  run: pipx install poetry
- run: poetry install --with dev
- run: poetry run pytest
```

`actions/setup-python@v6` supports `cache: poetry` if a `poetry.lock` is in the repo root.

## Standard CI pipeline

```yaml
name: CI
on:
  push: { branches: [main] }
  pull_request:

permissions:
  contents: read

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: astral-sh/setup-uv@SHA
        with: { enable-cache: true }
      - run: uv sync --dev
      - run: uv run ruff check .
      - run: uv run ruff format --check .

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: astral-sh/setup-uv@SHA
        with: { enable-cache: true }
      - run: uv sync --dev
      - run: uv run mypy src/

  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python: ['3.10', '3.11', '3.12', '3.13']
    steps:
      - uses: actions/checkout@v6
      - uses: astral-sh/setup-uv@SHA
        with: { enable-cache: true, python-version: '${{ matrix.python }}' }
      - run: uv sync --dev
      - run: uv run pytest --cov=src --cov-report=xml --junit-xml=junit.xml
      - if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results-py${{ matrix.python }}
          path: |
            junit.xml
            coverage.xml
```

## Linting: ruff

[ruff](https://docs.astral.sh/ruff/) is the de facto standard for Python linting and formatting in 2026. Replaces flake8, isort, pyupgrade, autoflake, pylint (mostly), and Black.

```yaml
- run: uv run ruff check .
- run: uv run ruff format --check .
```

Configure in `pyproject.toml`:
```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "B", "C4", "UP", "SIM"]
ignore = ["E501"]    # line-length handled separately
```

For inline annotations:
```yaml
- run: uv run ruff check --output-format=github .
```

`--output-format=github` emits annotations in GitHub Actions log format; lint failures show inline in the PR diff.

## Type checking: mypy, pyright

### mypy

```yaml
- run: uv run mypy src/
```

Configure in `pyproject.toml`:
```toml
[tool.mypy]
python_version = "3.13"
strict = true
warn_unused_ignores = true
```

For incremental performance in CI, cache mypy's incremental-check directory:
```yaml
- uses: actions/cache@v4
  with:
    path: .mypy_cache
    key: ${{ runner.os }}-mypy-${{ hashFiles('**/pyproject.toml', 'uv.lock') }}
- run: uv run mypy src/
```

### pyright

Faster than mypy; closer to type-checker behavior in IDEs (used by Pylance).

```yaml
- run: uv run pyright src/
# or
- uses: jakebailey/pyright-action@SHA   # pin
  with: { version: '1.1.391' }
```

The action variant adds inline annotations.

## Testing: pytest

```yaml
- run: uv run pytest --cov=src --cov-report=xml --cov-report=term-missing -n auto
```

Useful pytest flags:
- `-n auto` — pytest-xdist; parallelizes test execution across CPU cores.
- `--cov=src --cov-report=xml` — coverage report (XML for codecov, term for log).
- `--junit-xml=junit.xml` — JUnit-format report (consumed by GitHub's test summary).
- `--maxfail=5` — bail after N failures.
- `-x` — stop on first failure (useful for debugging in CI).

### Coverage upload

```yaml
- uses: codecov/codecov-action@SHA   # pin
  with:
    files: coverage.xml
    fail_ci_if_error: true
  env:
    CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
```

### Test sharding with pytest

pytest-split splits tests by historical timing:
```yaml
test:
  strategy:
    matrix:
      shard: [1, 2, 3, 4]
  steps:
    - run: uv run pytest --splits 4 --group ${{ matrix.shard }}
```

### Database/service tests

Use service containers:
```yaml
test:
  runs-on: ubuntu-latest
  services:
    postgres:
      image: postgres:16
      env: { POSTGRES_PASSWORD: postgres }
      ports: ['5432:5432']
      options: --health-cmd pg_isready --health-interval 10s --health-retries 5
  steps:
    - uses: actions/checkout@v6
    - uses: astral-sh/setup-uv@SHA
      with: { enable-cache: true }
    - run: uv sync --dev
    - env:
        DATABASE_URL: postgres://postgres:postgres@localhost:5432/postgres
      run: uv run pytest
```

## Version matrices

For libraries, test across Python versions and OSes:

```yaml
strategy:
  fail-fast: false
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
    python: ['3.10', '3.11', '3.12', '3.13']
    exclude:
      - { os: macos-latest, python: '3.10' }   # Python 3.10 wheels lacking on M1
runs-on: ${{ matrix.os }}
```

Trim the matrix to what's actually supported. Don't run all combinations if some are documented as unsupported.

## Publishing to PyPI

### Trusted Publishing (recommended; no API token)

PyPI side: Project → Publishing → Add a trusted publisher. Specify GitHub repo, workflow filename, and (optionally) environment.

Workflow side:

```yaml
name: Release
on:
  release:
    types: [published]

permissions:
  contents: read
  id-token: write     # required for OIDC

jobs:
  publish:
    runs-on: ubuntu-latest
    environment: pypi              # match the trusted publisher env if set
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with: { python-version: '3.13' }
      - run: pip install build
      - run: python -m build
      - uses: pypa/gh-action-pypi-publish@SHA   # pin to current SHA
        with:
          # No password needed when using Trusted Publishing
          packages-dir: dist/
```

### With API token (legacy)

```yaml
- uses: pypa/gh-action-pypi-publish@SHA
  with:
    password: ${{ secrets.PYPI_API_TOKEN }}
```

Generate a project-scoped token in PyPI account settings; store as a repo secret.

### Multi-arch wheels with cibuildwheel

For C-extension packages:

```yaml
build-wheels:
  strategy:
    matrix:
      os: [ubuntu-latest, ubuntu-latest-arm64, windows-latest, macos-latest]
  runs-on: ${{ matrix.os }}
  steps:
    - uses: actions/checkout@v6
    - uses: pypa/cibuildwheel@SHA   # pin
    - uses: actions/upload-artifact@v4
      with: { name: wheels-${{ matrix.os }}, path: ./wheelhouse/*.whl }

publish:
  needs: build-wheels
  runs-on: ubuntu-latest
  permissions: { id-token: write, contents: read }
  environment: pypi
  steps:
    - uses: actions/download-artifact@v5
      with: { pattern: wheels-*, path: dist/, merge-multiple: true }
    - uses: pypa/gh-action-pypi-publish@SHA
      with: { packages-dir: dist/ }
```

## Common gotchas

- **`pip install -e .` in CI works but is slow** — it builds the project on every run. Cache the venv or use `uv sync` for faster reinstalls.
- **`pip install` without a lockfile** introduces non-determinism. Use `pip install --require-hashes` with `pip-tools`-generated `requirements.txt`, or use `uv` / `poetry` which lock by default.
- **`pytest` exit codes:** `0` = all pass; `1` = some failed; `5` = no tests collected. A workflow that runs pytest in a directory with no tests gets exit `5` and fails. Be intentional about which directories you run.
- **Native deps in wheels** — manylinux on Linux runners works; macOS/Windows may need explicit toolchains. cibuildwheel handles this.
- **`actions/setup-python@v6` `cache: pip` requires `requirements*.txt` or `pyproject.toml`.** Otherwise no caching happens silently.
- **Avoid `pip install -U pip` in CI** — adds time, no value (the runner's pip is current enough).
- **Don't `chmod +x` Python scripts in CI** — use `python script.py` directly; permissions don't carry across runners reliably.
