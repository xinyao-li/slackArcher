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
- Assigned to an active maintainer, or claimed in comments within the last 30 days
- Module review health is **Closed** in the `project-brief` table
- Security-labeled, unless public and explicitly open to contributors

Apply the review-health filter the same way to every module. Do not keep a module with a large external backlog just because a maintainer is active there.

"No linked PR" means none was found. Also search comments, duplicate issues, similar PRs and recent commits. Record the search scope and time.

## 3. Rate

Rate every remaining candidate on both:

- Merge likelihood: run `merge-rate-score`.
- Impact: TODO, scorecard not yet designed.

## 4. Sort

- Sort by the chosen objective. Keep both ratings visible.
- Impact mode: drop candidates rated Low merge likelihood.
- Shortlist at most 10. If fewer than 5 remain, say the repo has too few eligible candidates and recommend trying another repo. Do not pad the list with Defer-rated issues; list them only if the user asks.
- If every shortlisted candidate has the same merge rating, state that the order comes from the tie-break (mostly impact), not from merge likelihood.

## Output

Header: search scope (issues, open and closed PRs, comments, recent commits), timestamp, and the review-health classification of each module that produced candidates.

For each candidate: issue, merge rating, impact rating, the signal values behind each rating, recommendation (Proceed / Investigate first / Confirm direction first / Defer), unknowns.

If no candidate is rated above Low in merge mode, say so and recommend a different repository before suggesting any next action in this one.
