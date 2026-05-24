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
    && ln -sf /usr/bin/batcat /usr/local/bin/bat \
    && rm -rf /var/lib/apt/lists/*

USER vscode
