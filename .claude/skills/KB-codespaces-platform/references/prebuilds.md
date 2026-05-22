# Prebuilds

Prebuilds snapshot a codespace's container *after* the slow setup steps, so new codespaces start from that snapshot. They turn 5-15 min creation into 30-60 sec creation for large repos.


## Contents

- [When prebuilds help](#when-prebuilds-help)
- [What runs during prebuild creation](#what-runs-during-prebuild-creation)
- [Configuration](#configuration)
- [Cost model](#cost-model)
- [How users get the benefit](#how-users-get-the-benefit)
- [Verifying it's working](#verifying-its-working)
- [Common pitfalls](#common-pitfalls)
- [Best practices](#best-practices)
- [Looking up current details](#looking-up-current-details)

## When prebuilds help

| Repo size / setup | Benefit |
|---|---|
| Creation > 2 minutes today | High -- the canonical threshold |
| Heavy `npm install` / `pip install` / `bundle install` / `cargo build` | High |
| Many features installed | High |
| Large clone (monorepo, big history) | High |
| Tiny repo + small image | Skip -- cost > benefit |

## What runs during prebuild creation

A GitHub Actions workflow creates a temporary codespace and runs:

1. Image pull / build
2. Feature installation
3. Repository clone
4. `onCreateCommand`
5. `updateContentCommand`

Then it snapshots the container and uploads to GitHub-managed storage.

**Not run during prebuild creation:**
- `postCreateCommand` (runs at codespace creation time, after snapshot is restored)
- `postStartCommand`, `postAttachCommand`
- Anything requiring **Docker-in-Docker** (DinD isn't initialized until after `onCreateCommand`)
- Anything requiring **secrets** (Codespaces user/repo secrets aren't available to the prebuild workflow by default)

**Implication:** any setup you want cached must live in `onCreateCommand` or `updateContentCommand` (or in the image itself).

## Configuration

Prebuilds are configured per-branch + per-`devcontainer.json` + per-region in **Repository Settings → Codespaces → Set up prebuild**:

1. Choose a **target branch** (typically `main` and any long-lived feature branches).
2. Choose the **dev container configuration file** (relevant for repos with multiple).
3. Choose **regions** to enable. Each region = separate storage cost.
4. Choose **trigger**:
   - `Every push` (default) -- freshest, most Actions minutes consumed
   - `On configuration change` -- only when `devcontainer.json` / Dockerfile / features change
   - `Scheduled` -- every N hours
5. Optional: **template repositories** -- list of repos to use this prebuild for if they're forks/templates.

When configured, GitHub creates a hidden `.github/workflows/codespaces-prebuilds-*.yml` workflow that orchestrates the build.

## Cost model

Two billing components:

| Component | Charged for |
|---|---|
| **GitHub Actions minutes** | Time spent building each prebuild |
| **Codespaces storage** | GB-hours of stored prebuild snapshot, per region, per active prebuild |

For high-traffic repos, storage cost per region can add up fast -- only enable regions that have actual users.

## How users get the benefit

When creating a codespace:
- If a prebuild is available for the branch + config + region, the user sees a **"Prebuild ready"** label in the machine-type picker.
- If a prebuild is mid-build, they see **"Prebuild in progress"** -- they can either wait or proceed without.
- If no prebuild matches (different branch, different config, different region), creation falls back to the slow path.

## Verifying it's working

```bash
# Did the user's most recent codespace use a prebuild?
gh codespace logs -c CODESPACE_NAME | grep -i prebuild

# Or in VS Code: Command Palette → "Codespaces: View Creation Log" → look for "prebuild"
```

The creation log shows `Setting up prebuilt codespace` if it hit; `Setting up new codespace` if it missed.

## Common pitfalls

- **Heavy work in `postCreateCommand`** → not cached. Move to `onCreateCommand` (if content-independent) or `updateContentCommand` (if content-dependent).
- **Secrets needed during build** → can't use them during prebuild. Either move to `postCreateCommand`, or for read-only registry credentials set them as **prebuild-permissible secrets** (org-level setting, see docs).
- **DinD pulls in `onCreateCommand`** → Docker daemon not running yet. Move to `postCreateCommand`.
- **Branch not enabled** → `feature/*` branches without prebuild config still take the slow path. Enable a wildcard or accept the cost.
- **Stale prebuilds** -- the prebuild workflow can fail silently. Check Actions tab; failures show as a banner on the codespace creation page.

## Best practices

- Enable prebuilds for `main` + any branch with >5 active developers.
- Enable only the regions where contributors actually live (check codespace location stats in Insights).
- Keep `onCreateCommand` deterministic -- non-determinism (e.g. fetching from a flaky API) causes flaky prebuilds.
- Use `updateContentCommand` for `npm ci` (or equivalent), not `onCreateCommand` -- content-dependent, but still cached in prebuild.
- Watch the prebuild workflow's runtime; if it grows past 30 min, profile and trim.

## Looking up current details

- **Region availability for prebuilds** -- query Context7 (`/websites/github_en` with `"prebuilds region availability"`) or `web_fetch` `docs.github.com/en/codespaces/prebuilding-your-codespaces`.
- **Spending limits / billing detail** -- see `org-management.md`.
