---
name: negative-eval
description: Rate a candidate issue's Risk (High / Medium / Low) of wasted or costly work. Used by screen-candidates and to re-rate after reproduce / analyze.
---

# Negative Eval

Risk means the cost of pursuing the issue, not a reason to exclude it. Every signal value carries an evidence tag: **Verified**, **Estimate** or **Unknown**, with its source.

Maintainers: `authorAssociation` OWNER / MEMBER / COLLABORATOR.
External: CONTRIBUTOR / FIRST_TIME_CONTRIBUTOR / NONE, excluding bots.

## Signals

| Signal | Values | Definition |
|---|---|---|
| Disputed | Yes / No | Maintainers disagree with the expected behavior or direction. |
| Scope | Local / Module / Cross-cutting | From file paths, stack traces, CODEOWNERS. Local: docs, tests, examples, one leaf file. Cross-cutting: public API, persistence, concurrency, multiple owners. Estimate at screen time. |
| Repro cost | Trivial / Setup | Setup: needs a build, fixtures or a service running locally. Special hardware or accounts are a user feasibility check in `screen-candidates`. |
| Review health | Healthy / Slow / Unresponsive / Insufficient evidence | From the `project-brief` module table for the issue's module. |
| Race risk | None / High | High if any: module flagged Owner-fixes in `project-brief`; P0/critical and unassigned with recent maintainer activity on the module; a maintainer merged changes to the same files in the last 7 days; an external contributor who opened or updated a PR on the module in the last 14 days commented on, reproduced or offered to fix the issue. Count distinct issues addressed, not PR count: stacked or consolidated PRs are one unit. |
| Stalled takeover | Yes / No | The candidate continues a stalled PR. |
| Long unresolved thread | Yes / No | >15 comments with no maintainer decision. |
| Maintenance branch | Yes / No | The fix targets a release or maintenance branch, not the default branch (from `screen-candidates`). |

## Rules

- **High** if any: Disputed; Race High; Review Unresponsive; Scope Cross-cutting confirmed by `analyze`.
- **Medium** if any: Review Slow, showing the median wait; Scope Cross-cutting (estimate); Stalled takeover; Long unresolved thread; Maintenance branch.
- **Low**: otherwise.

## Re-rating

After `reproduce` / `analyze`, re-rate with confirmed scope and repro. Unreproducible → High. Confirmed Cross-cutting with Agreement Confirmed → Medium.

Thresholds are initial guesses; tune on the historical evaluation.
