# Dockerfile for the `app` service in the compose-based dev container.
ARG NODE_VERSION=22
FROM mcr.microsoft.com/devcontainers/typescript-node:1-${NODE_VERSION}-bookworm

# Add tools used by postCreateCommand and dev workflows.
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

USER node
