---
name: merge
description: Run tests, squash-merge the open PR, pull master, and reset dev branch
disable-model-invocation: true
allowed-tools: Bash(git *, gh *, uv *, cd *, npm *)
---

# Merge PR and Reset

## Current state

!`git branch --show-current`
!`gh pr list --head dev --base master --state open --json number,title,url 2>/dev/null`

## Instructions

1. Find the open PR for dev → master:
   ```bash
   gh pr list --head dev --base master --state open --json number,title,url
   ```
   If no open PR exists, abort with an error message.

2. Run the test suite and abort if tests fail:
   ```bash
   uv run pytest
   ```

3. Squash-merge the PR:
   ```bash
   gh pr merge NUMBER --squash --delete-branch
   ```
   This will also delete the remote `dev` branch.

4. Switch to master and pull:
   ```bash
   git checkout master
   git pull
   ```

5. Delete the local dev branch if it still exists:
   ```bash
   git branch -D dev 2>/dev/null || true
   ```

6. Report success with the merged PR URL and the new commit on master.
