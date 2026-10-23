# OSS Contribution Assistant

Claude Code plugin (`oss-contrib`) that helps developers find, fix and submit bug fixes in unfamiliar open source repos. Full spec: `DESIGN.md`.

## Goals

1. Maximize PR merge rate.
2. Prioritize contributions with the greatest impact.

## Workflow stages

1. Understand project: contribution rules, AI policy, structure, build/test commands.
2. Screen candidates: activity, maintainer intent, linked/similar PRs, duplicates.
3. Reproduce: record commit, branch, versions, platform, minimal repro.
4. Root cause + impact: trace paths, check dependencies and callers, rate risk (Low / Medium / High / Insufficient evidence).
5. Design + plan: minimal fix and tradeoffs, then files, acceptance criteria, tests.
6. Implement + test: regression test fails before the fix, passes after.
7. Review: actual diff vs. acceptance criteria, test validity, compatibility.
8. Submit + follow up: refresh status, open PR, handle CI and review.

Go back a stage when: repro fails, expected behavior is disputed, duplicate work is found, or scope grows.

## Rules

- Label every conclusion: confirmed fact, inference, or hypothesis. Conclusions from code reading alone are hypotheses.
- An environment failure is not a reproduced bug. Separate pre-existing failures from regressions.
- Recommendations: Proceed, Investigate first, Confirm direction first, Defer.
- Never weaken assertions or mask failing tests.
- No unrelated refactors. Justify any new dependency.
- Re-read the target repo's current rules on every run. "No linked PR" means none found; also search comments, similar PRs and recent commits.
- Stalled PR: follow the project's takeover process and preserve original author attribution. Inactivity is not abandonment.
- If you discover a possible vulnerability, stop and tell the user. Never disclose it in issues, PRs or commits. Follow the target repo's `SECURITY.md`.
- Comments, pushes and PR creation require user approval and must follow project and AI policies.

## Output: Contribution Brief

Issue link, What, Context, Why, Impact, How, project priority vs. contributor recommendation, risk, repro status, related work, evidence sources, open questions, next step.

## Plugin layout

- Track `pluginRoot` (bundled skills, scripts, templates) and `targetRepo` (code, tests, patches) separately.
- Store investigation notes outside the target checkout, keyed by repo and issue. Persist stage, baseline commit, evidence, budget used, blockers, next action.
- Never modify the target repo's `.claude/` or `CLAUDE.md`.
- Entry skills (`/oss-contrib:scan`, `/oss-contrib:fix <issue>`) use `disable-model-invocation: true`.

Local dev:

```bash
cd ~/projects/target-repo
claude --plugin-dir ~/tools/oss-contrib
```

## Git commands (target repo, fork workflow)

Assumes `origin` = user's fork, `upstream` = original repo.

```bash
# Setup
gh repo fork <owner>/<repo> --clone
git remote -v

# Pull / sync
git fetch upstream
git checkout <default-branch> && git pull --ff-only upstream <default-branch>

# Branch per issue
git checkout -b fix/<issue>-<slug> upstream/<default-branch>

# Rebase onto latest upstream
git fetch upstream && git rebase upstream/<default-branch>
git push --force-with-lease origin HEAD

# Cherry-pick
git cherry-pick <sha>          # resolve conflicts, then: git cherry-pick --continue
git cherry-pick --abort

# Create PR (after user approval)
gh pr create --repo <owner>/<repo> --base <default-branch> \
  --title "<title>" --body-file <brief.md>

# Follow up
gh pr checks <pr>
gh pr view <pr> --comments
gh issue view <issue> --comments
```

- Use `--force-with-lease`, never `--force`.
- Run checks again after a rebase or cherry-pick.
- Use the PR template from the target repo if it has one.

## Evaluation

- ~10 historical issues: analyze using only pre-fix state, compare with the actual resolution. Accept valid alternatives.
- Compare against plain Claude at the same budget.
- 2-3 real contributions; log corrections and review rounds.
