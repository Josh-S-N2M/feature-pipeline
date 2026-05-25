ARG PYTHON_VERSION=3.11
FROM mcr.microsoft.com/devcontainers/python:1-${PYTHON_VERSION}-bookworm

# Remove the stale Yarn apt source shipped in the base image
# (broken GPG key — root cause of build failure).
RUN rm -f /etc/apt/sources.list.d/yarn.list

# Install pipeline tools at image-build time (cached, no rebuild cost).
RUN apt-get update && apt-get install -y --no-install-recommends \
    ripgrep \
    jq \
    bat \
    tree \
    less \
    shellcheck \
    curl \
    ca-certificates \
    && ln -sf /usr/bin/batcat /usr/local/bin/bat \
    && rm -rf /var/lib/apt/lists/*

# Install `uv` (Astral Python package manager) system-wide.
# Required by the canonical Serena MCP install path:
#   uv tool install serena-agent==${SERENA_VERSION} --prerelease=allow
# (Upstream Serena README explicitly disrecommends the `uvx --from git+...` form
# per the MCP-provisioning-postmortem 2026-05-24 review.)
RUN curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh

USER vscode
