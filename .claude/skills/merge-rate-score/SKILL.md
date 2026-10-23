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
| Review health | Healthy / Slow | Healthy: ≥2 external PRs merged on the same paths in 6 months, median first review ≤14 days. |
| Race risk | None / High | High: P0/critical, unassigned, recent maintainer activity. |
| Familiarity | Yes / No | User has a merged PR on the same paths. |

## Rules, in order

1. **Low** if any: Agreement Disputed; Scope Cross-cutting; Review Slow; Repro Special env; Race High; Agreement None and thread >15 comments with no maintainer decision.
2. **High** if all: Agreement Confirmed; Clarity Clear; Scope Local, or Module with Familiarity Yes; Repro Trivial or Setup; Review Healthy.
3. Otherwise **Medium**.
4. Cap at Medium: Agreement or Review health unknown; stalled PR takeover.
5. Tie-break within a tier: Familiarity, cheaper repro, smaller scope, more recent maintainer confirmation.

## Re-rating

After `reproduce` / `analyze`, re-rate with confirmed scope and repro. In merge mode, Cross-cutting or unreproducible → Low, recommend Defer.

Thresholds are initial guesses; tune on the historical evaluation.
