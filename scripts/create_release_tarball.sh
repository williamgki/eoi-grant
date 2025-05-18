#!/usr/bin/env bash
set -euo pipefail

# Determine repository root
REPO_ROOT="$(git rev-parse --show-toplevel)"
TARBALL="${1:-eoi-grant.tar.gz}"

# Create the tarball excluding the .git directory
cd "$REPO_ROOT"

tar --exclude=.git -czf "$TARBALL" .

echo "Created $TARBALL"
