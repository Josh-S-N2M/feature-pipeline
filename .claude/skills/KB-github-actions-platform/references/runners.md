# Runners

A runner is the machine that executes a job. Picking the right runner type matters for cost, performance, security, and capability. This reference covers the four flavors and when to use each.

## Table of contents

- [The four runner types](#the-four-runner-types)
- [GitHub-hosted runners](#github-hosted-runners)
- [Larger runners](#larger-runners)
- [Self-hosted runners](#self-hosted-runners)
- [Actions Runner Controller (ARC)](#actions-runner-controller-arc)
- [Choosing a runner](#choosing-a-runner)
- [Targeting runners with labels](#targeting-runners-with-labels)

## The four runner types

| Type | Hosted by | Hardware | Cost | Use when |
|---|---|---|---|---|
| **GitHub-hosted (standard)** | GitHub | 4-core, 16 GB RAM, ~14 GB SSD | Included free tier + per-minute | Default; most workflows |
| **GitHub-hosted (larger)** | GitHub | 4–96 cores, GPU options, more RAM | Per-minute (more expensive) | Heavy builds, GPU workloads, ARM |
| **Self-hosted** | You | Whatever you provision | Your infra cost | Need internal network access, custom hardware, persistent caches |
| **ARC (Kubernetes)** | You (in K8s) | Pod-based | Your cluster cost | Same as self-hosted but at scale, ephemeral, autoscaled |

## GitHub-hosted runners

The default. Specify with the `runs-on:` label:

```yaml
runs-on: ubuntu-latest    # current Ubuntu LTS, typically 24.04 in 2026
runs-on: ubuntu-24.04     # specific version (more reproducible)
runs-on: ubuntu-22.04
runs-on: macos-latest     # M1 ARM, on the M1 hardware tier
runs-on: macos-14         # specific macOS version
runs-on: windows-latest   # Windows Server 2022 currently
runs-on: windows-2022
```

### Specs (standard)

- 4 vCPU, 16 GB RAM, ~14 GB SSD usable
- Ubuntu, macOS, Windows
- Pre-installed software: Node, Python, Go, Java, .NET, Docker, gcloud, aws-cli, az, terraform, and more (full list in [actions/runner-images](https://github.com/actions/runner-images))
- Fresh VM per job; no state carries over

### Pros / cons

✅ Zero ops, ephemeral, broad pre-installed tooling, secure defaults
❌ Limited specs, no internal-network access, billing for private repos beyond free tier

### Pinning vs latest

`ubuntu-latest` is convenient but can shift unexpectedly when GitHub bumps the alias. For reproducibility-sensitive jobs (release builds), pin to a specific version: `ubuntu-24.04`.

## Larger runners

Configurable, more powerful runners managed by GitHub. Configured at the org/enterprise level.

### Capabilities

- Up to 96 vCPU
- Up to 384 GB RAM
- ARM64 Linux options
- GPU (NVIDIA T4, A10G)
- Static IPs (for whitelisting)
- Custom images (build once, reuse across runs)

### Use when

- Builds that don't fit in 4 cores / 16 GB.
- Workloads that benefit from ARM64 (lower per-minute cost on ARM).
- GPU jobs (ML training, CUDA tests).
- Need static outbound IP for cloud-side allowlists.

### How to target

Configured runners get custom labels. Pick one:

```yaml
runs-on: ubuntu-latest-16-core
runs-on: my-org-arm64
runs-on: gpu-large
```

Larger runners are billed per-minute at higher rates than standard. Check current pricing.

## Self-hosted runners

You provision the hardware (VM, container, bare metal). The GitHub Actions runner agent connects out to GitHub.

### Setup outline

1. Repo/org/enterprise → Settings → Actions → Runners → Add new self-hosted runner.
2. Run the install script on the target machine. It registers with GitHub and starts polling for jobs.
3. In a workflow, target it: `runs-on: [self-hosted, linux, x64]`.

### Use when

- Need internal-network access (private databases, internal package registries, on-prem services).
- Need specific hardware (huge RAM, specialized GPUs, FPGAs).
- Want persistent caches (e.g., a giant `node_modules` cache that doesn't fit in `actions/cache`).
- Compliance requirements (data must not leave your infrastructure).

### Risks (read [security.md](security.md))

- **Never use self-hosted runners on public repositories.** Anyone who can open a PR can run code on your runner. This is GitHub's explicit warning.
- Persistent state between jobs is a risk: prior secrets in env, leftover files, modified system state. Use ephemeral runners or aggressively reset.
- Network position: a self-hosted runner inside your VPC has the same access as anything else there.

### Hardening

- Run as a non-root user with limited sudo.
- Wipe the workspace between jobs (`actions/checkout` does this for the workspace, but not for `/tmp`, `~`, or system state).
- Use ephemeral mode: each runner accepts one job then deregisters. Prevents state leakage.
- Restrict network egress to what's needed (GitHub Actions APIs, your registries, etc.).
- Keep the runner agent up to date.

## Actions Runner Controller (ARC)

Kubernetes operator that runs ephemeral self-hosted runners as pods, autoscaling on demand. The modern way to operate self-hosted runners at scale.

### Architecture

- Runner Scale Set: a group of runners with shared config.
- Listener pod: watches GitHub for job demand and scales the runner pods.
- Runner pods: ephemeral; each takes one job and terminates.

### When to use

- You need self-hosted runner capabilities (network access, custom hardware) but at higher concurrency.
- You're already on Kubernetes and want pod-based isolation.
- You want true ephemerality at scale (pod-per-job, no leftover state).

### Authentication

ARC connects to GitHub via a GitHub App or Personal Access Token. App is preferred for org-wide deployments.

```yaml
# values.yaml for the gha-runner-scale-set Helm chart
githubConfigUrl: "https://github.com/my-org"
githubConfigSecret:
  github_app_id: "..."
  github_app_installation_id: "..."
  github_app_private_key: |
    -----BEGIN RSA PRIVATE KEY-----
    ...
runnerScaleSetName: "my-org-arc"
maxRunners: 50
minRunners: 0
template:
  spec:
    containers:
    - name: runner
      image: ghcr.io/actions/actions-runner:latest
```

In workflows:

```yaml
runs-on: my-org-arc
```

### Trade-offs vs static self-hosted

- More moving parts (Helm chart, the controller, the listener, the runners).
- Requires K8s knowledge.
- Better isolation (pod-per-job).
- Better autoscaling (you don't pay for idle).
- Easier image management (update the runner pod template, all new runners pick it up).

## Choosing a runner

```
Need access to internal network or specific hardware?
├── YES → self-hosted (or ARC if at scale)
└── NO → Continue
        Workflow needs more than 4 cores or 16 GB RAM?
        ├── YES → Larger runner
        └── NO → Continue
                Public repo?
                ├── YES → GitHub-hosted (never self-hosted)
                └── NO → GitHub-hosted (default; cheapest, simplest)
```

## Targeting runners with labels

`runs-on:` accepts a string, a list of labels, or a group/labels object.

```yaml
# Single label
runs-on: ubuntu-latest

# Multiple labels — runner must have ALL of them
runs-on: [self-hosted, linux, x64, gpu]

# Runner group + labels (for larger or self-hosted runner groups)
runs-on:
  group: gpu-runners
  labels: [self-hosted, gpu, cuda-12]
```

Multiple labels are AND-combined: the job runs on a runner that has every label in the list.

### Standard self-hosted labels

When you register a self-hosted runner, it's automatically labeled:
- `self-hosted`
- OS: `linux`, `windows`, `macOS`
- Arch: `x64`, `arm`, `arm64`

You can add custom labels at registration or in the runner UI. Use them to differentiate runner pools (`gpu`, `production`, `eu-region`).

### Matrix on runner type

```yaml
strategy:
  matrix:
    runner: [ubuntu-latest, ubuntu-latest-arm64, macos-14]
runs-on: ${{ matrix.runner }}
```

This is how you build cross-platform release artifacts.
