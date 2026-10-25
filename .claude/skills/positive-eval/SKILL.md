---
name: positive-eval
description: Learn which external contributions a repository accepts from its merged history, then rate each candidate issue's Opportunity. Used by screen-candidates.
---

# Positive Eval

Every signal value carries an evidence tag: **Verified**, **Estimate** or **Unknown**, with its source.

## Part 1: Acceptance profile (once per repository)

Reuse the per-PR classification from `project-brief`; do not refetch.

Qualifying merges: external PRs merged in the last 12 months, the 20 most recent, excluding the non-evidence merges listed by `project-brief` (vendor integrations, maintainer-invited PRs, bots).

For each qualifying merge, extract:

| Dimension | What to record |
|---|---|
| Problem type | Regression, compatibility, error handling, performance, docs, tests, etc. (Estimate) |
| Module | Where external contributions are actually accepted |
| User impact | Which use case, failure or pain point was addressed |
| Maintainer intent | Confirmed the problem, invited the fix, or set the direction |
| Change scope | Local fix, module-internal change, public interface change |
| Acceptance process | Major rewrites, the final accepted approach, what review asked to remove |

Read full review threads only for PRs in modules that have candidates after the hard filters.

Also list Rejected: quality and Rejected: owner fixed PRs as counterexamples.

### Output

- **Contribution fit**: 3-5 patterns of external contributions that get accepted. Each pattern: description, PRs, time range, sample size. A pattern with <3 PRs is **tentative**.
- **Maintainer priority**: what maintainers currently value, from milestones, explicit maintainer requests and recent maintainer comments. Merge counts alone do not establish priority.
- Counterexamples: what was rejected and why.

## Part 2: Opportunity (per candidate)

| Signal | Values | Definition |
|---|---|---|
| Pattern match | Strong / Partial / None | Strong: same module and problem type as a non-tentative pattern. Partial: one of the two matches. Tentative patterns are shown but do not count. |
| Agreement | Confirmed / Implicit / None | Confirmed: maintainer said bug is real or PR welcome, or applied `help wanted` in a repo that uses it. Implicit: maintainer opened or triaged it. Disputed is a Risk signal. |
| Invitation | Yes / No | A maintainer explicitly invited a fix on this issue in the last 90 days. Yes implies Agreement Confirmed. |
| Clarity | Clear / Partial / Unclear | Clear: expected vs actual behavior or acceptance criteria stated. |
| Minimal fix path | Text | Shown as a hypothesis; not scored. |

Rules:

- **High**: Pattern Strong, Agreement Confirmed, Clarity Clear.
- **Medium**: two of: Pattern Strong or Partial; Agreement Confirmed; Clarity Clear.
- **Low**: otherwise.

Candidates with Pattern None are **exploratory**.
