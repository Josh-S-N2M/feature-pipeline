# Organization Management -- Billing, Policies, Access

Available on **GitHub Team** and **GitHub Enterprise Cloud** plans. Personal accounts pay for their own codespaces; orgs can opt to pay for members'.


## Contents

- [Enabling for an org](#enabling-for-an-org)
- [Spending limit](#spending-limit)
- [Machine type policy](#machine-type-policy)
- [Image policy](#image-policy)
- [Idle timeout / retention policy](#idle-timeout-retention-policy)
- [Port-forwarding visibility policy](#port-forwarding-visibility-policy)
- [Audit log events](#audit-log-events)
- [Billing components](#billing-components)
- [Cost-control patterns](#cost-control-patterns)
- [Forcing changes on members](#forcing-changes-on-members)
- [API-driven org admin](#api-driven-org-admin)
- [Common policy questions](#common-policy-questions)

## Enabling for an org

Org Settings → Codespaces → **Codespaces general access**:

| Setting | Effect |
|---|---|
| **Disabled** | Members cannot create codespaces paid by the org. They can still create personal-paid codespaces against org repos. |
| **Selected members** | Whitelist who can create org-paid codespaces. |
| **Enabled for all members** | All org members. |

**Selected repos** further narrows which repos the org pays for.

## Spending limit

Org Settings → Billing → **Codespaces spending limit**:

- Set in USD. **`$0` = effectively disabled.**
- When hit, **new codespace creation is blocked** for org-paid usage; existing running codespaces continue until idle-stop, then can't restart on org's bill.
- Members fall back to personal billing (if their account allows).

Monitor via `GET /orgs/{org}/codespaces/billing` (admin-only).

## Machine type policy

Org Settings → Codespaces → **Policies** → **Add policy** → "Machine types":

- Pick allowed SKUs (e.g. permit only `basicLinux32gb` and `standardLinux32gb` to control cost).
- Apply org-wide or scope to specific repos.
- **Repo-specific overrides** can further restrict but not expand.
- Policies only apply to **org-paid** codespaces; user-paid against the same repo are unaffected.

Recommended starting policy: org-wide cap at `standardLinux32gb`, with explicit exceptions for ML/build-heavy repos.

## Image policy

Same Policies UI → "Base image":

- Restrict which base images are allowed.
- Use to enforce: only company-curated images, only `mcr.microsoft.com/devcontainers/*`, etc.
- Codespaces with a `devcontainer.json` referencing a disallowed image will fail to create.

## Idle timeout / retention policy

Two more policy types:

| Policy | Caps user setting at... |
|---|---|
| Maximum idle timeout | This many minutes (default user is 30; cap might be e.g. 60) |
| Maximum retention period | This many days (default user is 30; cap might be e.g. 7 to control storage cost) |

Lower retention = aggressive storage cost control (stopped codespaces auto-delete sooner).

## Port-forwarding visibility policy

Some plans allow restricting "public" port visibility org-wide. Check current availability via:

- Context7: `/websites/github_en` query `"organization codespaces port visibility policy"`.
- Fallback: `web_fetch` `docs.github.com/en/codespaces/managing-codespaces-for-your-organization/restricting-the-visibility-of-forwarded-ports`.

## Audit log events

Org audit log includes Codespaces events under the `codespaces.*` action type:

- `codespaces.create`
- `codespaces.start`
- `codespaces.stop`
- `codespaces.delete`
- `codespaces.create_an_org_secret`
- `codespaces.update_an_org_secret`
- `codespaces.remove_an_org_secret`
- `codespaces.update_org_settings`

Filter in **Org → Settings → Logs → Audit log** with `action:codespaces.*`.

Stream to S3/Splunk via the audit log streaming feature (Enterprise).

## Billing components

Two charges, on top of plan inclusions:

| Component | Unit | Notes |
|---|---|---|
| **Compute** | Per machine-type-hour while running | Bill stops the moment a codespace transitions to Stopped. |
| **Storage** | GB-hour for the codespace's storage **plus** any prebuild snapshots | Continues to accrue while Stopped. Stops at Delete. |

Spending limit covers both.

GitHub Team and Enterprise plans include some monthly free Codespaces hours/storage per seat -- check current allowances via Context7 (`"Codespaces free hours storage per plan"`) or the billing docs.

## Cost-control patterns

| Goal | Lever |
|---|---|
| Prevent runaway usage | Spending limit + machine type policy |
| Reduce idle waste | Lower org idle timeout cap (e.g. 30 → 15 min) |
| Reduce storage cost | Lower retention cap (30 → 7 days) |
| Reduce prebuild cost | Enable prebuilds only on `main` + only in actively-used regions |
| Identify expensive repos | `GET /orgs/{org}/codespaces/billing` + per-repo breakdown |
| Identify idle big-machine users | Org Codespaces dashboard → sort by machine type, last-used |

## Forcing changes on members

Admins can:

- **Stop** any member's codespace (`POST /orgs/{org}/members/{username}/codespaces/{name}/stop`)
- **Delete** any member's codespace (`DELETE /orgs/{org}/members/{username}/codespaces/{name}`)

Use sparingly -- destroys uncommitted work in `/workspaces`. Always notify the user first.

## API-driven org admin

| Task | Endpoint |
|---|---|
| List all org codespaces | `GET /orgs/{org}/codespaces` |
| List one member's codespaces | `GET /orgs/{org}/members/{username}/codespaces` |
| Stop a member's codespace | `POST /orgs/{org}/members/{username}/codespaces/{name}/stop` |
| Delete a member's codespace | `DELETE /orgs/{org}/members/{username}/codespaces/{name}` |
| Manage org-level Codespaces secrets | `/orgs/{org}/codespaces/secrets/...` |
| Get org billing | `GET /orgs/{org}/codespaces/billing` |

For full schemas: Context7 `/websites/github_en` with the path, or `web_fetch` `docs.github.com/en/rest/codespaces/organizations`.

## Common policy questions

**Q: Can I force every codespace in our org to use one specific base image?**
A: Yes -- add a base image policy listing only the approved image. Repos with non-conforming `devcontainer.json` will fail to create org-paid codespaces.

**Q: Can I require prebuilds for certain repos?**
A: No direct policy. You can enforce via repo-level required status checks on `devcontainer.json` changes and CODEOWNERS review.

**Q: Can I block public port forwarding org-wide?**
A: On supported plans, yes -- port visibility policy. Verify current availability via the docs.

**Q: Can I set Codespaces secrets org-wide that all repos auto-receive?**
A: Yes -- org-level Codespaces secrets with `visibility: all` (or `selected` repos). They appear as env vars in any codespace created in those repos.
