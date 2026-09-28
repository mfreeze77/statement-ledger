#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
repo="${1:-mfreeze77/statement-ledger}"
[[ "$repo" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]] || { echo "Expected owner/new-repository-name." >&2; exit 1; }
command -v git >/dev/null || { echo "Install Git first." >&2; exit 1; }
project_root="$(pwd -P)"
if git rev-parse --show-toplevel >/dev/null 2>&1; then
  test "$(git rev-parse --show-toplevel)" = "$project_root" || { echo "Refusing: this directory is inside a different Git repository." >&2; exit 1; }
fi
command -v gh >/dev/null || { echo 'Install GitHub CLI and run gh auth login first.' >&2; exit 1; }
gh auth status
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git init -b main
fi
if git remote get-url origin >/dev/null 2>&1; then
  echo 'Refusing: origin already exists. This script only creates a NEW repository.' >&2; exit 1
fi
if test -n "$(git status --porcelain)"; then
  echo 'Commit or remove outstanding changes before publishing; no files are auto-added.' >&2; exit 1
fi
if ! git rev-parse HEAD >/dev/null 2>&1; then
  echo 'Create the initial commit with your chosen Git author before publishing.' >&2; exit 1
fi
gh repo create "$repo" --private --source . --remote origin --push
