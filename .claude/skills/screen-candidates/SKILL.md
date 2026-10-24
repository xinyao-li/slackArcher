---
name: screen-candidates
description: Filter open issues, rate Opportunity, Risk and Confidence, and recommend a next action for each. Stage 2 of the contribution workflow.
---

# Screen Candidates

Requires the output of `project-brief`.

## 1. Ask the user

Objective:

- **Highest merge chance**: small, wanted, easy to review
- **Greatest impact**: not yet available (impact scorecard TODO). Say so and continue with highest merge chance.

Environment: "Do you have any special setup? (OS, GPU or hardware, cloud accounts)". Flag issues that need a setup the user lacks as "Cannot reproduce with your setup"; never recommend Proceed for them.

## 2. Hard filters

Drop the issue if any apply:

- Contribution type not accepted, or forbidden by the AI / contribution policy
- Module review health is **Closed** (policy excludes external contributions) in the `project-brief` table
- Closed or duplicate
- Linked or similar PR already in progress in the target repository. References from other repositories (forks, downstream projects) are not fixes: record them as downstream workarounds and do not filter on them.
- Labeled wontfix, not-a-bug, needs-design or needs-RFC
- Assigned to an active maintainer, or claimed in comments within the last 30 days
- Security-labeled, unless public and explicitly open to contributors

A maintainer invitation on the issue never overrides a policy that excludes the module.

"No linked PR" means none was found. Also search comments, duplicate issues, similar PRs and recent commits. Record the search scope and time.

## 3. Target branch

For each remaining candidate, check whether the code the issue names (files, functions) exists on the default branch. Use `gh api` or remote-tracking refs; do not change the working tree or local branches.

- Exists on the default branch → target the default branch.
- Missing there but present on a release or maintenance branch → record **Target branch: `<branch>`**.
- Missing on every maintained branch → drop as "code removed".

## 4. Evaluate

- Run `positive-eval` Part 1 once, then Part 2 for each remaining candidate → **Opportunity**.
- Run `negative-eval` for each remaining candidate → **Risk**.

## 5. Confidence

Key signals: Agreement, Review health, Scope.

- **High**: acceptance profile has ≥3 qualifying merges, and all key signals are Verified.
- **Low**: ≥2 key signals Unknown; or Review health Insufficient evidence and Invitation No.
- **Medium**: otherwise.

Unknown lowers Confidence; it is not Risk.

## 6. Next action

First match wins:

1. Risk High → **Defer**
2. Agreement None or Unknown → **Confirm direction first**
3. Confidence Low → **Investigate first**
4. Opportunity Medium or High → **Proceed**
5. Otherwise → **Defer**

## 7. Sort

- Order: Opportunity (High first), then Risk (Low first), then Confidence (High first), then Familiarity (user has a merged PR on the same paths), cheaper repro, more recent maintainer confirmation.
- At most 2 exploratory candidates, labeled.
- Shortlist at most 10. If fewer remain, report the actual count. Do not pad the list with Defer candidates; list them only if the user asks.

## Output

Show only these two parts. Collected data (review health, acceptance profile, signal values and evidence) supports the decision; show it only if the user asks.

1. One table:

| Issue | Opportunity | Confidence | Recommendation |
|---|---|---|---|

Recommendation: Next action and a one-line reason. Name the target branch when it is not the default branch.

2. Final recommendation: what to do next. If every candidate's Next action is Defer, say so and recommend a different repository.
