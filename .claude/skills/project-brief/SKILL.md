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
  --jq '.[] | select(.merged_at != null) | [.number, .author_association, .created_at, .merged_at] | @tsv'
gh api --paginate 'repos/<owner>/<repo>/pulls?state=open&per_page=100' \
  --jq '.[] | [.number, .author_association, .created_at] | @tsv'
```

2. Group by module: the first one or two path segments of the changed files (`gh pr view <n> --json files`). Use CODEOWNERS boundaries when present, and merge directories that are one unit (for example a source tree and its generated mirror). Cap at the 100 most recent open and 100 most recent merged external PRs; one `gh pr view` per PR costs about 0.7s.
3. For each module record: external merged, external open, backlog ratio (open : merged), median days to first review when available.
4. Classify:

| Health | Rule |
|---|---|
| Healthy | ≥2 external merged in 6 months, backlog ≤10:1, median first review ≤14 days |
| Slow | ≥2 external merged in 6 months, but backlog >10:1 or median first review >14 days |
| Closed | <2 external merged in 6 months, or backlog >10:1 with no external review activity in 30 days |

5. Flag merges that do not count as evidence for a bug-fix contributor: vendor adding their own integration, maintainer-invited PRs, bot PRs. List them separately.

Record the measurement time. Ratios and thresholds are initial guesses; tune on the historical evaluation.

## Output

Repository brief and contribution constraints:

- Contribution types the project accepts from external contributors
- AI policy requirements
- Required labels, acceptance criteria and disclosures
- Module structure
- Review health table by module (Healthy / Slow / Closed, with the counts behind it and the measurement time)
- Build and test commands
