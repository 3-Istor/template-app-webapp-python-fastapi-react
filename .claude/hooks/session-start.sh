#!/bin/sh
# SessionStart: pull main when it is safe, then list open PRs. stdout becomes
# context for the agent; this hook never fails the session.
cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

branch=$(git branch --show-current)
if ! git fetch --quiet --prune origin 2>/dev/null; then
  echo "git fetch failed: the code may not be current."
elif [ "$branch" = main ] && [ -z "$(git status --porcelain)" ]; then
  if git pull --quiet --ff-only 2>/dev/null; then
    echo "main is up to date: $(git log -1 --format='%h %s')"
  else
    echo "main could not be fast-forwarded to origin/main: check before starting."
  fi
else
  echo "On $branch with $(git rev-list --count HEAD..origin/main) commit(s) of origin/main missing; not pulled (local changes or not on main)."
fi

command -v gh >/dev/null 2>&1 || { echo "gh is not installed: list the open PRs another way."; exit 0; }
if prs=$(gh pr list --state open --limit 20 --json number,title,headRefName,author,files \
  --jq '.[] | "#\(.number) \(.title) [\(.headRefName), by \(.author.login)] files: \([.files[].path] | .[:8] | join(", "))"' 2>/dev/null); then
  if [ -n "$prs" ]; then
    echo "Open pull requests; read those that touch your files before starting:"
    echo "$prs"
  else
    echo "No open pull request."
  fi
else
  echo "Could not list pull requests (gh not signed in?): check them before starting."
fi
exit 0
