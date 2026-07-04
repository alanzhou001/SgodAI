#!/usr/bin/env bash
set -euo pipefail

REPO_NAME="${1:-SgodAI}"
VISIBILITY="${VISIBILITY:-public}"

if ! gh auth status >/dev/null 2>&1; then
  echo "GitHub CLI is not authenticated. Run: gh auth login -h github.com -p https -w"
  exit 1
fi

if git remote get-url origin >/dev/null 2>&1; then
  echo "origin already exists: $(git remote get-url origin)"
  git push -u origin main
else
  gh repo create "${REPO_NAME}" \
    "--${VISIBILITY}" \
    --source=. \
    --remote=origin \
    --push
fi

echo "Repository tracking:"
git branch -vv

