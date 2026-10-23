---
name: merge-rate-score
description: Rate an issue's merge likelihood as High / Medium / Low using the merge-rate scorecard. Used by screen-candidates and to re-rate after reproduce / analyze.
---

# Merge-Rate Score

Maintainers: `authorAssociation` OWNER / MEMBER / COLLABORATOR.
External: CONTRIBUTOR / FIRST_TIME_CONTRIBUTOR / NONE, excluding bots.

## Signals

| Signal | Values | Definition |
|---|---|---|
| Agreement | Confirmed / Implicit / None / Disputed | Confirmed: maintainer said bug is real or PR welcome, or applied `help wanted` in a repo that uses it. Implicit: maintainer opened or triaged it. |
| Clarity | Clear / Partial / Unclear | Clear: expected vs actual behavior or acceptance criteria stated. |
| Scope (estimate) | Local / Module / Cross-cutting | From file paths, stack traces, CODEOWNERS. Local: docs, tests, examples, one leaf file. Cross-cutting: public API, persistence, concurrency, multiple owners. |
| Repro cost | Trivial / Setup / Special env | Special env: hardware, cloud accounts, unavailable OS. |
| Review health | Healthy / Slow / Closed | Taken from the `project-brief` module table for the issue's module. Closed means external PRs there are effectively not reviewed; `screen-candidates` drops these before rating. |
| Race risk | None / High | High if any: P0/critical and unassigned with recent maintainer activity on the module; a maintainer merged changes to the same files in the last 7 days; an external contributor who opened or updated a PR on the module in the last 14 days commented on, reproduced or offered to fix the issue. Count distinct issues addressed, not PR count: stacked or consolidated PRs are one unit. |
| Familiarity | Yes / No | User has a merged PR on the same paths. |

## Rules, in order

1. **Low** if any: Agreement Disputed; Scope Cross-cutting; Review Slow; Repro Special env; Race High; Agreement None and thread >15 comments with no maintainer decision.
2. **High** if all: Agreement Confirmed; Clarity Clear; Scope Local, or Module with Familiarity Yes; Repro Trivial or Setup; Review Healthy.
3. Otherwise **Medium**.
4. Cap at Medium: Agreement or Review health unknown; stalled PR takeover.
5. Tie-break within a tier, in order: Familiarity Yes; higher impact rating; cheaper repro; smaller scope; more recent maintainer confirmation.

When every candidate lands in the same tier, say so in the output: the order then comes from the tie-break, mostly impact, not from merge likelihood.

## Re-rating

After `reproduce` / `analyze`, re-rate with confirmed scope and repro. In merge mode, Cross-cutting or unreproducible → Low, recommend Defer.

Thresholds are initial guesses; tune on the historical evaluation.
