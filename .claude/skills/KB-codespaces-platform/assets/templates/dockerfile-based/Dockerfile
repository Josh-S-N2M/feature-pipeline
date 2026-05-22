# Custom devcontainer Dockerfile.
# Build on a maintained dev container base so common-utils etc. layer cleanly on top.
ARG NODE_VERSION=22
FROM mcr.microsoft.com/devcontainers/typescript-node:1-${NODE_VERSION}-bookworm

# Install system packages not available as a Feature.
# Use --no-install-recommends to keep image lean. Clean apt lists at end of layer.
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Examples — replace with what you actually need:
    libpq-dev \
    postgresql-client \
    jq \
    # End examples
    && rm -rf /var/lib/apt/lists/*

# Optional: install an internal CLI from a tarball.
# RUN curl -fsSL https://internal.example.com/cli/v1.2.3/cli-linux-amd64.tar.gz \
#       | tar -xz -C /usr/local/bin \
#     && chmod +x /usr/local/bin/cli

# Optional: corporate CA cert.
# COPY corp-ca.crt /usr/local/share/ca-certificates/corp-ca.crt
# RUN update-ca-certificates

# Drop back to the non-root user (the base image's USER directive may have switched to root
# for the apt-get steps; explicit USER here makes intent clear).
USER node
