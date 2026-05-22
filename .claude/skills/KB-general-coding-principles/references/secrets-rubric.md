# Secrets Rubric

## Contents

- Credential shape patterns
- What counts as "real" vs "placeholder"
- Recommended placeholder patterns by context
- What the reviewer does
- Why even fake credentials matter

Patterns that match credential shapes, and the rules for handling them in design-time samples.

This file is consulted by dimension 5 of the scoring rubric and by the auto-fail rule in SKILL.md.

## Credential shape patterns

The following regex-like shapes are treated as credential-shaped. A string matching any of these triggers dimension-5 scoring and may trigger auto-fail.

| Pattern | Shape | Auto-fail if real |
|---|---|---|
| AWS access key | `AKIA[A-Z0-9]{16}` or `ASIA[A-Z0-9]{16}` | Yes |
| AWS secret key (paired with access key) | 40-char base64ish following an access key | Yes |
| GitHub personal access token (classic) | `ghp_[A-Za-z0-9]{36}` | Yes |
| GitHub fine-grained PAT | `github_pat_[A-Za-z0-9_]{82}` | Yes |
| GitHub OAuth token | `gho_[A-Za-z0-9]{36}` | Yes |
| GitHub user-to-server token | `ghu_[A-Za-z0-9]{36}` | Yes |
| GitHub server-to-server token | `ghs_[A-Za-z0-9]{36}` | Yes |
| GitHub refresh token | `ghr_[A-Za-z0-9]{36}` | Yes |
| Stripe live key | `sk_live_[A-Za-z0-9]{24,99}` | Yes |
| Stripe restricted live key | `rk_live_[A-Za-z0-9]{24,99}` | Yes |
| Stripe test key (still flag) | `sk_test_[A-Za-z0-9]{24,99}` | No, but score 0–3 |
| Slack token | `xox[abprs]-[A-Za-z0-9-]{10,}` | Yes |
| Google API key | `AIza[A-Za-z0-9_-]{35}` | Yes |
| OpenAI API key | `sk-[A-Za-z0-9]{32,}` | Yes |
| Anthropic API key | `sk-ant-[A-Za-z0-9-_]{80,}` | Yes |
| Generic JWT | three base64url segments separated by `.` | If realistic claims |
| Private key PEM (covers RSA, EC, DSA, OpenSSH, and unencrypted PKCS#8 variants) | begins with five hyphens, then `BEGIN`, then a key-type token in `[A-Z ]+`, then `PRIVATE KEY` and five hyphens | Yes, always |
| Generic bearer token | 32+ char base64ish high-entropy string in `Authorization: Bearer ...` context | Probably — investigate |

## What counts as "real" vs "placeholder"

**Real:** the string would actually authenticate against the named service if presented. Auto-fail; rewrite is required regardless of intent.

**Realistic-looking placeholder:** matches a shape pattern, is NOT a live credential, but a reader would have to verify that to know. Score 0–3, surface as `important` issue, recommend rewrite.

**Unmistakable placeholder:** matches no shape pattern, or includes a marker that reveals it's fake (`<TOKEN>`, `xxx`, `***`, `EXAMPLE`, `REPLACE_ME`, the literal string `placeholder`). Score 7–10.

**Reference to a secret store:** the sample shows where the secret comes from instead of the secret itself (`${{ secrets.GITHUB_TOKEN }}`, `process.env.STRIPE_KEY`, `os.environ['DB_PASSWORD']`). Score 10.

## Recommended placeholder patterns by context

```yaml
# YAML / GitHub Actions
env:
  TOKEN: ${{ secrets.MY_TOKEN }}              # canonical
  TOKEN: ${{ vars.MY_PUBLIC_VAR }}            # for non-secret config
```

```python
# Python
api_key = os.environ["STRIPE_API_KEY"]        # canonical
api_key = "<set via env: STRIPE_API_KEY>"     # if showing the shape inline
```

```bash
# Shell
export TOKEN="$STRIPE_API_KEY"                # canonical — read from caller's env
export TOKEN="REPLACE_ME"                     # acceptable inline if shape doesn't matter
```

```typescript
// TypeScript / JavaScript
const apiKey = process.env.STRIPE_API_KEY!;   // canonical with explicit non-null
```

## What the reviewer does

When `shared-document-reviewer` runs Gate 1 on a document:

1. Scan all code fences for the shape patterns above
2. For each match:
   - If `<>`-wrapped or `${{ secrets.* }}` or `os.environ[...]`: pass
   - If contains literal `EXAMPLE`, `xxx`, `***`, `REPLACE_ME`: pass with note
   - Otherwise: flag for verification
3. For flagged matches, run revocation check if a service-specific endpoint is available (e.g. GitHub `/user` with the token in a sandbox), OR escalate as `important` issue with text "string matches credential shape; verify before merge"
4. Real credentials → auto-fail document; do not score further until rewritten

## Why even fake credentials matter

Three reasons even "obviously fake" credentials trigger scoring < 10:

1. **Secret scanners can't tell.** GitHub's secret-scanning service and many SAST tools will flag the sample as a leaked secret regardless of whether the project intends it as a placeholder. False-positive triage cost.
2. **Copy-paste contamination.** Design docs get pasted into PR descriptions, Slack, runbooks. A realistic-looking credential propagates.
3. **Honest mistakes.** Sometimes the "fake" string was a real revoked token someone pasted. Even revoked tokens shouldn't propagate.

Use placeholders that no scanner and no reader could mistake for real.
