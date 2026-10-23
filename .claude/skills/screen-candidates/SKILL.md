---
name: screen-candidates
description: Filter and rank open issues by the user's objective (highest merge chance or greatest impact). Stage 2 of the contribution workflow.
---

# Screen Candidates

Requires the output of `project-brief`.

## 1. Ask the objective

Ask the user:

- **Highest merge chance**: small, wanted, easy to review
- **Greatest impact**: painful bug even if harder

## 2. Hard filters

Drop the issue if any apply:

- Contribution type not accepted, or forbidden by the AI / contribution policy
- Closed or duplicate
- Linked or similar PR already in progress
- Labeled wontfix, not-a-bug, needs-design or needs-RFC
- Assigned, or claimed in comments
- No external PRs merged in the module
- Security-labeled, unless public and explicitly open to contributors

"No linked PR" means none was found. Also search comments, duplicate issues, similar PRs and recent commits. Record the search scope and time.

## 3. Rate

Rate every remaining candidate on both:

- Merge likelihood: run `merge-rate-score`.
- Impact: TODO, scorecard not yet designed.

## 4. Sort

- Sort by the chosen objective. Keep both ratings visible.
- Impact mode: drop candidates rated Low merge likelihood.
- Shortlist 5-10.

## Output

For each candidate: issue, merge rating, impact rating, the signal values behind each rating, recommendation (Proceed / Investigate first / Confirm direction first / Defer), unknowns.
