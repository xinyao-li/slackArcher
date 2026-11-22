# Notes

Research findings that shape how the assistant works. Each entry: finding, evidence strength, source, and how we apply it. Applications are hypotheses until validated on real contributions.

## Maintainer interaction matters more than issue write-up

**Finding:** For a newcomer's first issue, social interaction matters more than how well the issue is written. Maintainer comments have a mostly monotonic positive effect on newcomer success and retention. Issue text length and readability have almost no effect.

**Evidence:** Strongest result in the study (E-value 2.24). 45,865 first issues across 777 repositories. Preprint, not peer reviewed. Sample includes only issues newcomers resolved, so it says nothing about comments that went unanswered.

**Source:** Hao et al., [The First Issue Matters: Linking Task-Level Characteristics to Long-Term Newcomer Retention in OSS](https://arxiv.org/html/2603.27136), arXiv 2603.27136, 2026.

**Application (starting point for `fix`):**

- Engage maintainers early, before investing in a full fix.
- Give concrete technical feedback: reproduction, root cause evidence, proposed approach. Not general offers to help.
- Treat maintainer engagement on an issue as a strong signal when selecting and pursuing work.
- Maintainer interaction rate with external contributors indirectly shows their attitude: actively open, or not paying much attention. Our inference; the study does not measure attitude.

## First human response drives PR outcomes; bots distort response metrics

**Finding:** Bots generate many of the fastest first responses (up to 97% of first responses in one project), so raw "time to first response" is misleading. Time to first *human* response explains 64.7% of PR lifetime variance; bot response time explains 0.33%. PRs with longer descriptions and larger changes wait longer for a human response. Many PRs that waited over a month were merged within a day once a reviewer looked, sometimes after the author pinged them.

**Evidence:** 111,094 closed PRs from 10 popular projects. Bot labels manually checked on 1,000 PRs (0.2% inconsistent). Data from 2019, before GitHub Actions and AI-generated PRs were common. PRs with no response at all are excluded.

**Source:** Hasan et al., [Understanding the Time to First Response In GitHub Pull Requests](https://arxiv.org/pdf/2304.08426), arXiv 2304.08426, 2023.

**Application:**

- Exclude bots when measuring maintainer response rate and latency. Bots such as `k8s-ci-robot` can carry MEMBER association and make a module look healthier than it is. This is a bug in `project-brief`.
- Keep PRs small with concise descriptions; they get faster human responses.
- A long wait is not a rejection. In `submit`, a polite ping after a reasonable wait is justified.

## Why external PRs get rejected

**Finding:** Developers whose PRs were never merged are common: about 70% as many as successful contributors, and 85% try only once. The top reasons for rejection are superseded or duplicate work (top in both the survey and manual review), a mismatch with the team's vision, and PRs judged not needed. Maintainers rank "not needed" and "guidelines not followed" first. Other reasons: the contributor did not follow up on review feedback, missing tests, side effects, code that became obsolete within days, and maintainers implementing the idea themselves. Trivial PRs (e.g. adding one comma) are seen as noise. About 30% of rejected contributors said rejection discouraged further contributions.

**Evidence:** ICSE 2018, peer reviewed. 10,099 never-merged contributors with 12,367 PRs across 21 popular projects; 263 PRs coded by three researchers to consensus. Survey response rates are low (6.5% of contributors, 21 maintainers), and 13% of respondents said they were misidentified. Data up to 2017. The paper's conclusion names "vision mismatch" as the top reason, but its own table and manual review put "superseded/duplicate" first.

**Source:** Steinmacher et al., [Almost There: A Study on Quasi-Contributors in Open Source Software Projects](https://www.marcoagerosa.com/papers/icse2018-Pinto.pdf), ICSE 2018.

**Application:**

- Most rejection reasons are already covered: existing-PR filter and race risk (duplicates), Disputed and "Confirm direction first" (vision), Agreement (not needed), Owner-fixes (maintainer implements it), reading CONTRIBUTING (guidelines), regression tests, target-branch check and refresh before submit (obsolete code).
- Gap: `submit` must follow up on review feedback point by point.
- Gap: distinguish small from trivial. A small fix to a real bug is good; wording-only or punctuation PRs are often rejected as noise. `positive-eval` should not favor trivial changes.
- Side effects and missing tests are explicit rejection reasons; some projects close PRs without tests immediately. Both belong in the PR checklist below.

## Contributors check for duplicates before coding, but not before submitting

**Finding:** Most contributors look for related issues and recent PRs before coding, but 59% never or rarely tell the core team what they plan to do, and most do not recheck for duplicate work before submitting. Contributors communicate intended changes mainly by opening an issue (~75%) or a minimal PR that describes the problem and fix (~70%). The top challenge is social, led by poor responsiveness: over 100 respondents complained, and "rejected is better than ignored." Contributors say even acknowledging an issue and suggesting an approach helps greatly. Discussion often moves to channels outside GitHub. Maintainers, in the companion study, complain about "hit-and-run" PRs whose authors disappear after change requests.

**Evidence:** ICSE 2016, peer reviewed. Survey of 645 top-3 contributors to 3,400 active repositories (18% response rate). Self-reported. Respondents are experienced contributors, not newcomers. No coding agreement metric; 25% of answers came through unsolicited forwarding. Data from 2014.

**Source:** Gousios et al., [Work Practices and Challenges in Pull-Based Development: The Contributor's Perspective](https://repository.tudelft.nl/record/uuid:d8992914-323a-42b2-8ea5-f34b17aa42b2), ICSE 2016.

**Application:**

- A minimal PR that states the problem and fix is a common, accepted way to communicate. In repos with low comment response, prefer it over waiting on a comment.
- Recheck for duplicate or superseded work right before submitting.
- GitHub-only response metrics undercount maintainer engagement. `project-brief` should find the project's channels (e.g. Discord) in CONTRIBUTING and note them.
- Stay available after submitting and answer review promptly; avoid hit-and-run.

## Learn from who actually resolved issues, not from labels

**Finding:** Only 1.93% of issues carry a good-first-issue label, and only 21% of labeled issues are actually resolved by newcomers. Issues newcomers resolve tend to have longer descriptions with links and code snippets, reporters with moderate project experience, participation from experienced developers (e.g. labeling), and a project owner who is active and has onboarded newcomers before. Competition is real: 98.85% of issues resolved within two hours go to experienced developers, and 61% of issues reported by experienced developers are resolved by the reporter. In a field test, researchers suggested labels on 60 issues to maintainers; 33 (55%) got a response and 16 were confirmed.

**Evidence:** ICSE 2022, peer reviewed, artifacts available and reusable. 53,510 resolved issues from the 100 projects with the most good-first-issue labels, so the sample favors projects that welcome newcomers. Issue state restored to two historical time points to avoid future-data leakage. Field test is small. Data from 2021.

**Source:** Xiao et al., [Recommending Good First Issues in GitHub OSS Projects](https://hehao98.github.io/files/2022-recgfi.pdf), ICSE 2022.

**Application:**

- Supports `positive-eval` learning from merged external PRs rather than labels.
- Supports trusting `help wanted` only in repos that actually use it.
- Restoring historical issue state is the method for the backtest layer of the AI eval.
- Conflict with current rules: `positive-eval` counts a maintainer-opened issue as Agreement Implicit (positive), but maintainers resolve most issues they report themselves (race risk). Distinguish an issue a maintainer opened and left from one they are working on.
- Simple new issues are claimed quickly by experienced developers; issue freshness matters for race risk.
- 55% response to outside suggestions is the closest data point so far for comment response rate, from newcomer-friendly projects and for labeling suggestions, not offers to fix.
- Candidate `positive-eval` signals: reporter with moderate experience, experienced developers participating, active owner who has onboarded newcomers.

## PR checklist (for the create-PR skill)

Check every PR the assistant creates. Sources in brackets refer to the entries above.

| Check | Pass when | Source |
|---|---|---|
| Tests | A regression test fails on the original code and passes with the fix; relevant existing tests pass | Rejection reasons; contributor practice |
| Side effects | No behavior change outside the issue's scope; callers and public contracts reviewed | Rejection reasons |
| Self-contained | The diff changes only what the issue needs; no unrelated refactors | Contributor practice |
| Not trivial | Fixes real behavior, not wording or punctuation only | Rejection reasons |
| Guidelines | Follows the repo's style, commit format, PR template and required disclosures | Rejection reasons; contributor practice |
| No duplicate | No open or merged PR in the target repo addresses the same issue, checked just before and after opening | Rejection reasons; contributor practice |
| Not obsolete | Based on the current target branch; the changed code still exists there | Rejection reasons |
| Small and clear | Small diff; description states the problem, the fix and how it was verified | Time to first response |
| Follow-up | Every review comment answered; ping once after a reasonable wait | Rejection reasons; time to first response; contributor practice |
