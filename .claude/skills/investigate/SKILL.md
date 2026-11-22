---
name: investigate
description: Reproduce a selected issue, find its root cause and assess the impact of a fix. Stages 3-4 of the contribution workflow.
---

# Investigate

Scripts collect and execute; you write the reproduction and draw conclusions. Run `scripts/investigate.py` in this skill's directory with `python3 -I`. Evidence goes to `~/.oss-contrib/<owner>__<repo>/<issue>/`; never write to the target repository's working tree.

Every conclusion carries an evidence tag: **Verified** (shown by a run), **Estimate**, or **Hypothesis** (code reading only).

Ask the user before installing dependencies or running the target repository's code. Show the exact commands.

v1 supports Node and Python repositories.

## Phase 1: Reproduce

1. `baseline --repo <repo> --branch <target-branch> --issue <n>`: record commit, versions, OS.
2. `workspace --repo <repo> --branch <target-branch> --issue <n>`: isolated worktree on the target branch.
3. Read the issue and find evidence for the expected behavior: docs, tests, maintainer statements.
4. Write a minimal reproduction in the worktree, preferably as a failing test that can become the regression test.
5. `run --repo <repo> --issue <n> --label <label> --cwd <worktree> -- <command>`: run it.
6. `classify --record <run-record>`: heuristic category. Confirm it yourself.

| Result | Next |
|---|---|
| Reproduced | Phase 2 |
| Environment failure | Not a reproduced bug. Record what was tried; retry within the investigation budget, then pause |
| Not reproduced | Record what is missing; Risk High; recommend Defer or a question to the reporter |

## Phase 2: Root cause and impact

1. Form hypotheses about the cause.
2. `context --repo <worktree> --paths <files> [--lines <a,b>]`: recent commits, blame, CODEOWNERS, related tests.
3. If several hypotheses fit, design small experiments and run them with `run`.
4. State the root cause and why a fix there covers the original trigger.
5. `impact --repo <worktree> --symbol <name>`: internal references to each symbol the fix changes. The scan over-collects; read only the snippets and classify every site:
   - **Affected**: depends on the behavior that changes
   - **Unaffected**: uses only what stays the same
   - **Unsure**: needs a closer look
   Drop false positives (same name, different symbol; comments; dead code). Report "N scanned → M affected, K unsure". The scan is a lower bound: note dynamic calls, string imports or plugin systems if the repo uses them.
6. Confirm Scope (Local / Module / Cross-cutting) and re-run `negative-eval`. If the scope grows, return to the user before planning.

## Output

To the user, briefly: reproduction status, root cause with its evidence tag, affected sites, re-rated Risk and Next action. Keep the full evidence in the evidence directory. Reproduction and root-cause evidence can strengthen the suggested comment to maintainers.
