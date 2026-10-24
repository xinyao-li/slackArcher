# OSS Contribution Assistant

Claude Code skills that find, fix and submit bug fixes in open source repositories. Design: `DESIGN.md`.

Status: first draft. Only `scan` is implemented.

## Requirements

- [Claude Code](https://code.claude.com)
- `git`
- [GitHub CLI](https://cli.github.com), logged in:

```bash
gh auth login
gh auth status
```

## Install

Link the skills into your user skills folder so they load in any repository:

```bash
mkdir -p ~/.claude/skills
for s in /path/to/slackArcher/.claude/skills/*; do
  ln -s "$s" ~/.claude/skills/
done
```

Symlinks pick up edits to this repo without reinstalling. Restart Claude Code after installing.

Uninstall:

```bash
for s in /path/to/slackArcher/.claude/skills/*; do
  rm ~/.claude/skills/"$(basename "$s")"
done
```

## Usage

```bash
git clone https://github.com/<owner>/<repo>.git
cd <repo>
claude
```

In Claude Code:

```text
/scan
```

`scan` will:

1. Read the repo's contribution rules, AI policy, structure and build/test commands.
2. Ask your objective and your special setup (OS, hardware, cloud accounts).
3. Filter out ineligible issues, learn what external contributions the repo accepts, and rate the rest.
4. Show up to 10 candidates in one table (Issue, Opportunity, Confidence, Recommendation), then a final recommendation. Ask for the data behind any rating.

## Skills

| Skill | Role |
|---|---|
| `scan` | Entry point. User-invoked only. |
| `project-brief` | Stage 1: eligibility and constraints. |
| `screen-candidates` | Stage 2: filter and rank issues. |
| `positive-eval` | Acceptance profile and Opportunity rating. |
| `negative-eval` | Risk rating. |

## Known gaps

- Impact mode is not designed yet.
- Progress is not saved between sessions.
