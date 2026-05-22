# Dev Container Features

Features are reusable installation units distributed as OCI artifacts. They install tools, runtimes, or CLIs into a dev container without you writing Dockerfile RUN steps.

**Authoritative spec:** https://containers.dev/implementors/features/
**Public registry browser:** https://containers.dev/features
**Source repos:** https://github.com/devcontainers/features (official) and https://github.com/devcontainers-contrib/features (community)


## Contents

- [Syntax](#syntax)
- [Install order](#install-order)
- [Main features (what most projects need)](#main-features-what-most-projects-need)
- [Other features (when, why, lookup)](#other-features-when-why-lookup)
- [Feature options pattern](#feature-options-pattern)
- [Authoring custom features](#authoring-custom-features)
- [Common pitfalls](#common-pitfalls)

## Syntax

```jsonc
"features": {
  "ghcr.io/devcontainers/features/<name>:<version>": {
    "<option>": "<value>"
  }
}
```

- Version `1` accepts any 1.x release. Use `latest` only for experimentation.
- Options are feature-specific; consult the feature's README.

## Install order

Features are installed in an order chosen by the dev container CLI based on declared dependencies. **When a feature depends on another being present first** (e.g. installing a Node-based CLI requires Node), pin order explicitly:

```jsonc
"overrideFeatureInstallOrder": [
  "ghcr.io/devcontainers/features/common-utils",
  "ghcr.io/devcontainers/features/node",
  "ghcr.io/devcontainers/features/aws-cli"
]
```

## Main features (what most projects need)

### Universal infrastructure

- **`ghcr.io/devcontainers/features/common-utils:2`** -- sets up zsh/oh-my-zsh, common utilities, optional non-root user with sudo. **Include in nearly every project** unless using an image that already includes it.
- **`ghcr.io/devcontainers/features/git:1`** -- newer git than the OS package; usually unnecessary on `:bookworm` images that already have a recent git.
- **`ghcr.io/devcontainers/features/github-cli:1`** -- `gh` CLI. Useful when scripts in the codespace call GitHub APIs.

### Container-in-container

- **`ghcr.io/devcontainers/features/docker-in-docker:2`** -- runs a Docker daemon inside the container. Use when the project needs to build/run images. **Not available during `onCreateCommand`** -- pull images from `postCreateCommand` or later.
- **`ghcr.io/devcontainers/features/docker-outside-of-docker:1`** -- mounts the host's Docker socket. Lighter than DinD; the project's containers run as siblings on the host. Use when DinD's overhead isn't justified.

Pick exactly one; never both.

### Languages and runtimes (TypeScript-relevant)

- **`ghcr.io/devcontainers/features/node:1`** -- Node.js. Options: `version` (`lts`, `18`, `20`, `22`, etc.), `nodeGypDependencies`, `nvmInstallPath`. Skip if you're already using `mcr.microsoft.com/devcontainers/typescript-node:*` (it has Node baked in).
- **`ghcr.io/devcontainers-contrib/features/pnpm:2`** (community) -- pnpm package manager.
- **`ghcr.io/devcontainers-contrib/features/turborepo-npm:1`** (community) -- Turborepo CLI.

### Cloud and IaC

- **`ghcr.io/devcontainers/features/aws-cli:1`**
- **`ghcr.io/devcontainers/features/azure-cli:1`**
- **`ghcr.io/devcontainers/features/gcloud:1`**
- **`ghcr.io/devcontainers/features/terraform:1`** -- installs `terraform`, optionally `tflint` and `terragrunt`. Pin a major version.
- **`ghcr.io/devcontainers/features/kubectl-helm-minikube:1`**

### Quality / DX

- **`ghcr.io/devcontainers-contrib/features/pre-commit:2`** -- installs `pre-commit` framework.
- **`ghcr.io/devcontainers-contrib/features/act:1`** -- run GitHub Actions locally.

## Other features (when, why, lookup)

The full registry has 100+ features (Java, Python, Go, .NET, Ruby, Rust, PHP, databases, observability tools, etc.). For any feature not listed above:

1. **Why:** the user needs a specific tool/runtime not on this list and doesn't want to maintain Dockerfile RUN steps.
2. **When:** prefer a feature over a custom Dockerfile when one exists and is well-maintained -- features compose cleanly and version cleanly.
3. **Lookup protocol:**
   - **Context7 first:** library `/websites/github_en`, query `"devcontainer feature <name>"` or `"devcontainers features <topic>"`.
   - **Fallback 1:** `web_fetch` https://containers.dev/features (browse the registry).
   - **Fallback 2:** `web_fetch` the feature's README on GitHub (e.g. `https://github.com/devcontainers/features/tree/main/src/<name>`).

When suggesting a feature you've not personally verified, **say so** and cite the lookup source so the user can validate.

## Feature options pattern

Every feature exposes options as a JSON object. Defaults exist; only override what you need:

```jsonc
"features": {
  "ghcr.io/devcontainers/features/node:1": {
    "version": "22",
    "nodeGypDependencies": true
  },
  "ghcr.io/devcontainers/features/terraform:1": {
    "version": "1.9",
    "tflint": "latest",
    "installSentinel": false
  }
}
```

Discover options via the feature's README, or via the feature's `devcontainer-feature.json` in the source repo.

## Authoring custom features

For internal/private features:

```
my-feature/
├── devcontainer-feature.json   # metadata + options schema
├── install.sh                  # idempotent install script
└── README.md
```

Publish to a private OCI registry (GHCR works). Reference as `ghcr.io/myorg/features/my-feature:1`. See https://containers.dev/implementors/features/ for the manifest schema and best practices.

**Don't author a custom feature when:**
- A community/official feature already does the job.
- The install steps are tightly coupled to one project (use the Dockerfile instead).

**Do author when:**
- Your org has a tool 5+ projects need to install identically.
- You want versioned, controlled rollouts of internal CLIs.

## Common pitfalls

- **Layering Node feature onto an image that already has Node** → version conflict. Either drop the feature, or use a base image without Node.
- **Forgetting `overrideFeatureInstallOrder`** when feature B needs feature A installed first → flaky builds.
- **Pinning to a feature `:latest`** → prebuild snapshot bakes in whatever was current at prebuild time; new codespaces may differ from local rebuilds.
- **Chaining 8+ features** → slow installs, conflict surface area grows. Consider a custom base image instead.
