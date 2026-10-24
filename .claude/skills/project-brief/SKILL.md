---
name: project-brief
description: Determine whether and how an external contributor can contribute to the target repository. Stage 1 of the contribution workflow.
---

# Project Brief

Eligibility only. Do not rank issues here.

Read the current versions on every run:

- Contribution rules (`CONTRIBUTING.md`, PR template)
- AI / contribution policy
- Project purpose and module structure
- Build and test commands
- `SECURITY.md`

## Review health by module

Measure whether maintainers actually review outside PRs, per module. A repo-wide number hides modules that never merge external work.

Maintainers: `author_association` OWNER / MEMBER / COLLABORATOR. External: everything else, excluding bots.

1. Pull PRs from the last 6 months:

```bash
gh api --paginate 'repos/<owner>/<repo>/pulls?state=closed&per_page=100' \
  --jq '.[] | [.number, .author_association, .created_at, .closed_at, .merged_at] | @tsv'
gh api --paginate 'repos/<owner>/<repo>/pulls?state=open&per_page=100' \
  --jq '.[] | [.number, .author_association, .created_at] | @tsv'
```

2. Group by module: the first one or two path segments of the changed files (`gh pr view <n> --json files`). Use CODEOWNERS boundaries when present, and merge directories that are one unit (for example a source tree and its generated mirror). Cap at the 100 most recent open and 100 most recent closed external PRs; one `gh pr view` per PR costs about 0.7s.
3. Classify each external PR (`gh pr view <n> --json reviews,comments,closedAt,mergedAt`):

| Category | Detection |
|---|---|
| Merged | `merged_at` set |
| Reviewed, open | Open, with a maintainer review or comment |
| Rejected: quality | Closed unmerged after a maintainer review requesting changes, or a closing comment citing safety, tests or requirements |
| Rejected: owner fixed | Closed unmerged; a maintainer PR or commit fixed the same issue, or the closing comment says so |
| Rejected: unknown | Closed unmerged after a maintainer review, reason unclear |
| No response | Open or closed with no maintainer review or comment |

Responded = every category except No response.

4. For each module record: count per category, backlog ratio (open : merged), median days to first maintainer response.
5. Classify:

| Health | Rule |
|---|---|
| Closed | Contribution policy excludes external contributions to the module |
| Insufficient evidence | <3 external PRs in 6 months |
| Unresponsive | ≥3 external PRs, none responded |
| Slow | ≥3 external PRs, but backlog >10:1 or median first response >14 days |
| Healthy | ≥3 external PRs, backlog ≤10:1, median first response ≤14 days |

Flag the module **Owner-fixes** if Rejected: owner fixed is ≥2 PRs and ≥1/3 of its external PRs.

6. Flag merges that do not count as evidence for a bug-fix contributor: vendor adding their own integration, maintainer-invited PRs, bot PRs. List them separately.

Record the measurement time. Ratios and thresholds are initial guesses; tune on the historical evaluation.

## Output

For `screen-candidates`; do not present it to the user unless asked.

Repository brief and contribution constraints:

- Contribution types the project accepts from external contributors
- AI policy requirements
- Required labels, acceptance criteria and disclosures
- Module structure
- Review health table by module (Healthy / Slow / Unresponsive / Insufficient evidence / Closed, Owner-fixes flag, per-category counts, measurement time)
- Per-PR classification, kept for `positive-eval`
- Build and test commands
