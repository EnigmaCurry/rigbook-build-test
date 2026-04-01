---
name: status
description: "Show current branch, working tree status, and any open PR"
disable-model-invocation: true
allowed-tools: Bash(git *, gh *)
---

# Status

!`git branch --show-current`
!`git status --short`
!`gh pr list --author @me --state open --repo EnigmaCurry/rigbook --json number,title,url,headRefName,baseRefName`

Report the current branch, any uncommitted changes, and any open PRs. Keep it brief.
