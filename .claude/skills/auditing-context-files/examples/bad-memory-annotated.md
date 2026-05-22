# Memory Examples: Good and Bad (annotated)

## Contents

- The file (full source)
- Per-dimension findings
- Total and verdict
- What this calibrates

Examples of auto memory (and subagent persistent memory — the same rules apply) that illustrate the auditor's expectations.

## Good MEMORY.md (95+/100)

```audit-example -- negative-example annotated fixture demonstrating scanner-flagged content; documents what the auditor scanner detects
# Project memory

## Architecture summary

The service is event-driven with a Postgres outbox pattern. Events are
published to Redis Streams; consumers commit offsets before processing.

See topics/outbox-pattern.md for details.

## Recent decisions

- 2026-04: Adopted SQLAlchemy 2.0 async style throughout.
- 2026-03: Switched from Pydantic v1 to v2.

## Open questions

- Caching strategy for user lookups (see topics/caching.md).
- Whether to add CDC for analytics warehouse.

## Conventions learned

- The team prefers `match` over `if/elif` chains in Python.
- Tests use `respx` for HTTP mocking.
```

### Why this scores 95+

- 19 lines — well under the 200-line cap.
- Section headings provide scannable index.
- References to topic files are concise and resolve to files that exist.
- No credentials, no machine-local paths.
- Each section says what it is for.

## Bad MEMORY.md (FAIL)

```audit-example -- negative-example annotated fixture demonstrating scanner-flagged content; documents what the auditor scanner detects
# Memory

## What I learned today

I started by reading the README at /Users/alice/projects/svc/README.md.
Then I looked at the auth module and tried to figure out what was going on.
The user said to use the token github_pat_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA which seemed fine.

I tried running the tests but they failed because /home/alice/scripts/db.sh
wasn't there. I had to find that file first.

Then I worked on the auth module for a while. I made some changes. Then I
made some more changes. The user wasn't sure what they wanted. We talked
about it. They decided to keep it as it was.

Then I worked on the API tests. Some of them were failing. I fixed three
of them. I'm not sure why two of them keep failing; we should look at them
later.

(... continues for 400+ lines of similar log content ...)

## References

See topics/auth-changes.md for the auth work.
See topics/api-tests.md for the test fixes.
See src/auth/legacy.py for the old auth code.
```

### Findings

- **BLOCKER (SECURITY-BLOCK):** AM-2 credential capture — literal GitHub PAT in line 5.
- **MAJOR:** AM-5 machine-local paths — Users-style and home-style absolute paths.
- **MAJOR:** AM-6 oversized — described as 400+ lines (>200).
- **MAJOR:** AM-1 The Log — chronological narrative rather than index.
- **MINOR:** AM-3 stale references — topic-file citations to non-existent paths.
- **MINOR:** Project-file citation that may not resolve if files moved.

### Why this fails

The credential alone is SECURITY-BLOCK regardless of everything else. Even ignoring that:

- A 400-line MEMORY.md gets ~200 lines silently dropped at session load. Anything in the dropped region is invisible to Claude.
- The Log structure (AM-1) means the *most recent* content is at the end — exactly the content that gets dropped.
- Machine-local paths leak personal information and break if the memory is shared.

### Fixes

1. **Delete the credential immediately and rotate it.**
2. Run `/memory prune` to reset.
3. Ask Claude to rewrite MEMORY.md as a current-state index, not a log.
4. Move detail to topic files.
5. Replace absolute paths with relative ones.

## Calibration notes

- The pedagogical example uses `EXAMPLE`-style padding for the GitHub PAT (`AAAAAAA...`), which the anti-laundering check **would still flag** as a real-looking credential because the AAAA pattern doesn't contain any of the FAKE_CREDENTIAL_INDICATORS. **In tests, use `EXAMPLE` or `FAKE_GITHUB_PAT` suffix to make the marker check correctly demote.**
- Real-world MEMORY.md examples should never have any credential-shaped content. The example here triggers the scanner because that's its point — the auditor's test fixtures must include this kind of dangerous content to verify detection.
