# SHA Pins — pipeline-quickwins-hardening-r1

Resolved: 2026-05-26T00:00:00Z  
Resolver: execute-task-code-producer (T0.2)  
Consumed by: T3.1 (FR-5 workflow), T3.2 (FR-4c workflow)

---

## actions/checkout

| Field | Value |
|---|---|
| Tag family | v4 (latest: v4.3.1) |
| Pinned SHA | `34e114876b0b11c390a56381ad16ebd13914f8d5` |
| Lookup URL | `https://github.com/actions/checkout` |
| Verification command | `git ls-remote https://github.com/actions/checkout v4` |
| Expected output | `34e114876b0b11c390a56381ad16ebd13914f8d5  refs/tags/v4` |

Usage in workflow YAML:

```yaml
uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5  # v4.3.1
```

---

## devcontainers/ci

| Field | Value |
|---|---|
| Tag family | v0.3 (latest: v0.3.1900000449) |
| Pinned SHA | `b63b30de439b47a52267f241112c5b453b673db5` |
| Lookup URL | `https://github.com/devcontainers/ci` |
| Verification command | `git ls-remote https://github.com/devcontainers/ci v0.3` |
| Expected output | `b63b30de439b47a52267f241112c5b453b673db5  refs/tags/v0.3` |

Usage in workflow YAML:

```yaml
uses: devcontainers/ci@b63b30de439b47a52267f241112c5b453b673db5  # v0.3.1900000449
```

---

## Verification notes

Both SHAs were resolved on 2026-05-26 via `git ls-remote` against the canonical GitHub repositories. The `v4` tag and the `v4.3.1` annotated tag both dereference to the same commit (`34e11...`), confirming the pin tracks the current tip of the v4 release branch. The `v0.3` tag and `v0.3.1900000449` both dereference to `b63b30...`.

Re-verify before use if more than 30 days have elapsed since this file was written — floating tags can be re-pointed on new patch releases.
