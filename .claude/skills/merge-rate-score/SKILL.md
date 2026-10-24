---
name: merge-rate-score
description: Rate an issue's merge likelihood as High / Medium / Low using the merge-rate scorecard. Used by screen-candidates and to re-rate after reproduce / analyze.
---

# Merge-Rate Score

Ratings are an uncalibrated ranking: High is expected to merge more often than Medium, not a measured probability. State this in the output.

Maintainers: `authorAssociation` OWNER / MEMBER / COLLABORATOR.
External: CONTRIBUTOR / FIRST_TIME_CONTRIBUTOR / NONE, excluding bots.

## Signals

| Signal | Values | Definition |
|---|---|---|
| Agreement | Confirmed / Implicit / None / Disputed | Confirmed: maintainer said bug is real or PR welcome, or applied `help wanted` in a repo that uses it. Implicit: maintainer opened or triaged it. |
| Clarity | Clear / Partial / Unclear | Clear: expected vs actual behavior or acceptance criteria stated. |
| Scope (estimate) | Local / Module / Cross-cutting | From file paths, stack traces, CODEOWNERS. Local: docs, tests, examples, one leaf file. Cross-cutting: public API, persistence, concurrency, multiple owners. |
| Repro cost | Trivial / Setup | Setup: needs a build, fixtures or a service running locally. Whether the user has special hardware or accounts is a feasibility question for the user, not a merge signal. |
| Review health | Healthy / Slow / Closed / Insufficient evidence | Taken from the `project-brief` module table for the issue's module. Closed means external PRs there are effectively not reviewed; `screen-candidates` drops these before rating. |
| Invitation | Yes / No | Yes: a maintainer explicitly invited a fix on this issue in the last 90 days. |
| Race risk | None / High | High if any: module flagged Owner-fixes in `project-brief`; P0/critical and unassigned with recent maintainer activity on the module; a maintainer merged changes to the same files in the last 7 days; an external contributor who opened or updated a PR on the module in the last 14 days commented on, reproduced or offered to fix the issue. Count distinct issues addressed, not PR count: stacked or consolidated PRs are one unit. |
| Familiarity | Yes / No | User has a merged PR on the same paths. |

## Rules, in order

1. **Low** if any: Agreement Disputed; Race High; Agreement None and thread >15 comments with no maintainer decision.
2. **High** if all: Agreement Confirmed; Clarity Clear; Scope Local, or Module with Familiarity Yes; Review Healthy.
3. Otherwise **Medium**.
4. Cap at Medium: Agreement unknown; Scope Cross-cutting (estimate); Review Slow, showing the median wait; Review health unknown or Insufficient evidence, unless Invitation Yes; stalled PR takeover.
5. Tie-break within a tier, in order: Familiarity Yes; higher impact rating; cheaper repro; smaller scope; more recent maintainer confirmation.

When every candidate lands in the same tier, say so in the output: the order then comes from the tie-break, mostly impact, not from merge likelihood.

## Re-rating

After `reproduce` / `analyze`, re-rate with confirmed scope and repro. In merge mode, confirmed Cross-cutting without Confirmed agreement, or unreproducible → Low, recommend Defer. Confirmed Cross-cutting with Confirmed agreement stays capped at Medium.

Thresholds are initial guesses; tune on the historical evaluation.
