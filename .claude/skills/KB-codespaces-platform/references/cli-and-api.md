# `gh codespace` CLI and REST API


## Contents

- [`gh codespace` -- full subcommand surface](#gh-codespace-full-subcommand-surface)
- [REST API -- main endpoints](#rest-api-main-endpoints)
- [Other endpoints -- when, why, how to look up](#other-endpoints-when-why-how-to-look-up)
- [Encrypting secrets for the secrets API](#encrypting-secrets-for-the-secrets-api)
- [Pagination](#pagination)
- [Rate limiting](#rate-limiting)

## `gh codespace` -- full subcommand surface

Authenticate first: `gh auth login` with the `codespace` scope.

### Lifecycle

```bash
# Create
gh codespace create \
  --repo OWNER/REPO \
  --branch BRANCH \
  --machine standardLinux32gb \
  --location UsEast \
  --devcontainer-path .devcontainer/typescript/devcontainer.json \
  --display-name "feature-X work" \
  --idle-timeout 60m \
  --retention-period 7d

# List
gh codespace list                    # yours
gh codespace list --repo OWNER/REPO  # in a repo
gh codespace list --org ORG          # in an org (admin)

# Stop / start (start happens implicitly on ssh/code/connect)
gh codespace stop -c CODESPACE_NAME

# Rebuild
gh codespace rebuild -c CODESPACE_NAME            # rebuild container, keep cached image
gh codespace rebuild -c CODESPACE_NAME --full     # discard cached image too

# Delete
gh codespace delete -c CODESPACE_NAME
gh codespace delete --all                          # all yours (asks confirmation)
gh codespace delete --days-old 30                  # housekeeping
```

`-c CODESPACE_NAME` can be omitted on most commands -- `gh` opens an interactive picker.

### Connecting

```bash
# SSH into running codespace
gh codespace ssh -c CODESPACE_NAME

# Run a single command (non-interactive)
gh codespace ssh -c NAME -- "cd /workspaces/repo && npm test"

# Open in local VS Code
gh codespace code -c CODESPACE_NAME

# Open in VS Code Insiders
gh codespace code --insiders -c CODESPACE_NAME

# Open Jupyter (browser)
gh codespace jupyter -c CODESPACE_NAME
```

### Ports

```bash
# Forward LOCAL_PORT:REMOTE_PORT to your machine
gh codespace ports forward 3000:3000 -c CODESPACE_NAME

# List forwarded ports
gh codespace ports -c CODESPACE_NAME

# Set visibility
gh codespace ports visibility 3000:public -c CODESPACE_NAME      # anyone with URL
gh codespace ports visibility 3000:org -c CODESPACE_NAME         # org members
gh codespace ports visibility 3000:private -c CODESPACE_NAME     # default
```

### File transfer

```bash
# Local → codespace
gh codespace cp localfile.txt remote:/workspaces/repo/

# Codespace → local
gh codespace cp -r remote:/workspaces/repo/dist ./dist

# `remote:` prefix is required for the codespace side
```

### Diagnostics

```bash
# Tail creation log
gh codespace logs -c CODESPACE_NAME

# Save to file
gh codespace logs -c CODESPACE_NAME > /tmp/creation.log
```

### Editing

```bash
# Change machine type (applies on next start)
gh codespace edit -c CODESPACE_NAME --machine premiumLinux

# Rename
gh codespace edit -c CODESPACE_NAME --display-name "new name"
```

### Stop policies / view

```bash
# Show codespace details
gh codespace view -c CODESPACE_NAME --json state,machine,gitStatus,lastUsedAt
```

## REST API -- main endpoints

Base URL: `https://api.github.com`. Required headers on every request:

```
Accept: application/vnd.github+json
Authorization: Bearer <TOKEN>
X-GitHub-Api-Version: 2022-11-28
```

Token requirements: classic PAT with `codespace` scope, or fine-grained PAT with **Codespaces: Write** repository permission.

### List authenticated user's codespaces

```
GET /user/codespaces
```

Optional query: `repository_id` to filter, `per_page`, `page`.

### Get a codespace

```
GET /user/codespaces/{codespace_name}
```

Returns full state object: `state`, `machine`, `git_status`, `devcontainer_path`, `idle_timeout_minutes`, `retention_period_minutes`, `web_url`, etc.

### Create a codespace (in a repo)

```
POST /repos/{owner}/{repo}/codespaces
```

Body:

```json
{
  "ref": "main",
  "machine": "standardLinux32gb",
  "geo": "UsEast",
  "devcontainer_path": ".devcontainer/devcontainer.json",
  "display_name": "feature work",
  "idle_timeout_minutes": 60,
  "retention_period_minutes": 10080
}
```

Returns 201 with the codespace object including `name` (the immutable identifier).

### Create a codespace (for the user, by repo ID)

```
POST /user/codespaces
```

Body:

```json
{ "repository_id": 12345, "ref": "main" }
```

Or for a PR codespace:

```json
{
  "pull_request": {
    "pull_request_number": 42,
    "repository_id": 12345
  }
}
```

### Update a codespace

```
PATCH /user/codespaces/{codespace_name}
```

Body (any subset):

```json
{ "machine": "premiumLinux", "display_name": "renamed" }
```

Machine change applies on next start.

### Start / stop / delete

```
POST   /user/codespaces/{codespace_name}/start    # 204
POST   /user/codespaces/{codespace_name}/stop     # 204
DELETE /user/codespaces/{codespace_name}          # 202
```

### Example -- full request (cURL)

```audit-example -- Documents credential-shaped environment variable patterns the auditor flags via DE-2 scanner; pedagogical example of env-var-based credential handling, not real credentials.
curl -L -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -d '{"ref":"main","machine":"standardLinux32gb"}' \
  https://api.github.com/repos/OWNER/REPO/codespaces
```

## Other endpoints -- when, why, how to look up

These are real endpoints; details (params, response schemas) change. Use the listed source-of-truth lookup before relying on them.

| Endpoint | When to use |
|---|---|
| `GET /repos/{owner}/{repo}/codespaces/machines` | List available machine SKUs for a given repo + ref. Use before creating to validate `machine` value. |
| `GET /repos/{owner}/{repo}/codespaces/devcontainers` | List the devcontainer.json files in a repo. Use to drive a config picker. |
| `POST /user/codespaces/{name}/exports` | Export uncommitted changes when a user can't push (e.g. lost auth). |
| `POST /user/codespaces/{name}/publish` | Publish an unpublished codespace as a new repo. |
| `GET /user/codespaces/secrets` | List user-level Codespaces secrets. |
| `PUT /user/codespaces/secrets/{secret_name}` | Create/update a user-level secret (encrypts with public key). |
| `DELETE /user/codespaces/secrets/{secret_name}` | Remove a user-level secret. |
| `GET /repos/{owner}/{repo}/codespaces/secrets` | List repo-level Codespaces secrets. |
| `PUT /repos/{owner}/{repo}/codespaces/secrets/{name}` | Create/update repo-level secret. |
| `GET /orgs/{org}/codespaces` | List all codespaces in the org (admin). |
| `GET /orgs/{org}/codespaces/secrets` | List org-level Codespaces secrets. |
| `PUT /orgs/{org}/codespaces/secrets/{name}` | Create/update org-level secret. |
| `GET /orgs/{org}/codespaces/billing` | Org billing for Codespaces (admin). |
| `GET /orgs/{org}/members/{username}/codespaces` | List a member's codespaces (admin). |
| `DELETE /orgs/{org}/members/{username}/codespaces/{name}` | Force-delete a member's codespace (admin). |
| `GET /user/codespaces/{name}/machines` | Available machine types this codespace can move to. |
| `POST /repos/{owner}/{repo}/codespaces/permissions_check` | Check if user can create a codespace with given devcontainer's requested permissions. |

### Source-of-truth lookup for any of these

When sub-agent needs full request/response detail for any endpoint:

1. **Context7 first.** Library `/websites/github_en`. Query with the path: `"REST API codespaces /repos/{owner}/{repo}/codespaces/machines"` or similar.
2. **Fallback:** `web_fetch` `https://docs.github.com/en/rest/codespaces/codespaces` (or the matching subpage: `/codespaces/secrets`, `/codespaces/organizations`, `/codespaces/machines`).
3. **Cite which doc** in the response.

## Encrypting secrets for the secrets API

Both the user/repo/org secrets endpoints require the value to be **encrypted with the recipient's public key** before sending. The flow:

```bash
# 1. Get the public key
curl -H "Authorization: Bearer $TOKEN" \
  https://api.github.com/repos/OWNER/REPO/codespaces/secrets/public-key

# 2. Encrypt locally with libsodium / sodium-plus / similar (returns base64)

# 3. PUT the encrypted blob
curl -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"encrypted_value":"...","key_id":"..."}' \
  https://api.github.com/repos/OWNER/REPO/codespaces/secrets/MY_SECRET
```

The `gh secret set --app codespaces` command does this automatically.

## Pagination

Most list endpoints support `per_page` (max 100) and `page`. Follow `Link` header `rel="next"` for full enumeration.

## Rate limiting

Codespaces endpoints share GitHub's standard 5000/hr authenticated REST limit. Watch `X-RateLimit-Remaining`. For org-wide reporting jobs, batch creates and polls.
