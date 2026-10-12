---
name: review-doc-pr
description: Runs once per pull request and posts one advisory docs review comment. Reviews changed docs (accuracy, style, reference, clarity, completeness) and, when user-facing code changed, checks whether docs are missing and drafts them. Read-only, never applies fixes, never blocks merge. Product comes from a profile (`--profile proxy`). Invoke non-interactively as `/review-doc-pr <pr-number> --profile proxy`.
allowed-tools: "Read Grep Glob Bash(python3:*) Bash(git:*) Bash(gh:*)"
---

# review-doc-pr (profile-driven demo)

Demo copy of the Hub per-PR review skill, generalized with a **product profile**
(`profiles/<name>.json`): docs location, doc engine, style guide, which code counts
as user-facing, bot PRs to skip. The five review layers are product-neutral; only the
profile and the style checklist differ per product. See `README.md` for the design.

Read-only and advisory: never applies fixes, never edits the PR, never blocks merge.
Fires once per PR; the comment carries a marker so a CI retry skips instead of
duplicating (no edit-in-place).

## Bundled resources

- Scripts: `${CLAUDE_SKILL_DIR}/scripts/`, run as
  `PYTHONPATH="${CLAUDE_SKILL_DIR}" python3 -m scripts.<name>`.
  - `setup.py`: preflight (Step 0)
  - `profile.py`: loads `profiles/<name>.json` (Step 1)
  - `pr_filter.py`: skips dependency-bot PRs, profile-driven (Step 0)
  - `missing_docs.py`: classifies changed files into docs vs user-facing code and picks the path (Step 2)
  - `_discover.py`: repo root (Proxy: docs and source are the same repo) or a separate source clone (Hub)
  - `changed_lines.py`: per-file changed-line ranges (Step 2)
  - `_finding.py`, `check_links.py`, `run_style_lint.py`, `aggregate.py`, `_gh.py`, `_git.py`: shared engine
  - `post_review.py`: severity cap, render, post or skip (Step 6)
- References: `${CLAUDE_SKILL_DIR}/references/`: `finding-schema.md`, `accuracy-checklist.md`,
  `style-checklist.md` (Proxy rules), `reference-checklist.md`, `clarity-checklist.md`,
  `completeness-checklist.md`, `missing-docs-checklist.md` (new), `proxy-style-guide.md` (bundled fallback).
- Template: `${CLAUDE_SKILL_DIR}/templates/pr-comment.md.tmpl`.

Never `cd` into the skill directory. Run from the PR's checked-out branch.

## Step 0: Preflight and skip

```bash
PYTHONPATH="${CLAUDE_SKILL_DIR}" python3 -m scripts.setup --check --skip-git-check
gh pr view <pr> --json author,title --jq '{author: .author.login, title: .title}'
PYTHONPATH="${CLAUDE_SKILL_DIR}" python3 -m scripts.pr_filter --profile proxy \
  --author-login <login> --title <title>
```

Setup failure: stop and report it. `pr_filter` exit 1 (dependency bot or `chore(deps)` title):
stop, run no layer, post nothing.

## Step 1: Profile and source

```bash
PYTHONPATH="${CLAUDE_SKILL_DIR}" python3 -m scripts._discover repo-root
```

Profile `source: "self"` (Proxy): the code the accuracy layer checks against is this repo
at the PR head. Any other `source` value names a separate source repo: locate that clone, and
if it is not found, degrade every accuracy finding to `suggestion`, low confidence,
`unverifiable`. Never ask: no human is present.

## Step 2: Classify the PR

```bash
gh pr diff <pr> --name-only | PYTHONPATH="${CLAUDE_SKILL_DIR}" python3 -m scripts.missing_docs --profile proxy > classify.json
PYTHONPATH="${CLAUDE_SKILL_DIR}" python3 -m scripts.changed_lines \
  --repo-root <root> --base <pr-base-branch> --head <pr-head-branch> > changed-lines.json
```

`classify.json` `action`:

| action | Run | Post |
|---|---|---|
| `full-review` | Step 3 (all layers), and Step 3b if `run_missing_docs` | one comment |
| `missing-docs-only` | Step 3b only | a comment only if a gap was found |
| `silent` | nothing | nothing |

## Step 3: Review layers (docs changed)

All five layers run over `docs_changed`. Scope differs:

| Layer | Scope |
|---|---|
| Accuracy | Whole file. Evidence is the PR's code diff first, then surrounding code (struct, defaults, tests) |
| Reference: mechanical (`check_links.py`) and judgment | Whole file |
| Style (`references/style-checklist.md`, the Proxy style guide) | Diff-scoped: changed lines only |
| Clarity | Diff-scoped: changed lines only |
| Completeness | Whole file. Always `suggestion`, `auto_fixable: false` |

Each layer writes `<layer>.json` in the shape of `references/finding-schema.md`. If
`run_style_lint.py` ran, unwrap its dict output first; for Proxy no linter runs, so style is
agent-only and the comment says so. Validate every file:

```bash
PYTHONPATH="${CLAUDE_SKILL_DIR}" python3 -m scripts._finding <layer>.json
```

A finding that fails validation: re-prompt with the validator error, max 3 attempts, then
replace it with an `unverifiable` finding at the same location. Never fail the run over one finding.

## Step 3b: Missing-docs check (user-facing code changed)

Follow `references/missing-docs-checklist.md` for each `user_facing_code` entry. Write the
results as `completeness` findings (merge into `completeness.json` when both exist).
If `generated_touched` is non-empty, report it as the top style finding.

## Step 4: Cap severity outside the diff

Findings whose line is outside the PR's changed lines become `suggestion`. Nothing is dropped.
`post_review.py` applies this right before rendering.

## Step 5: Aggregate

```bash
PYTHONPATH="${CLAUDE_SKILL_DIR}" python3 -m scripts.aggregate \
  --accuracy accuracy.json --style style.json --reference reference.json --clarity clarity.json \
  --completeness completeness.json --template templates/pr-comment.md.tmpl --out merged.json --quiet
```

Always pass `--quiet`: the console echo is uncapped and can disagree with the posted comment.

## Step 6: Render and post

```bash
PYTHONPATH="${CLAUDE_SKILL_DIR}" python3 -m scripts.post_review \
  --repo <owner/repo> --pr <pr> --findings merged.json \
  --changed-lines changed-lines.json --template templates/pr-comment.md.tmpl
```

Add `--dry-run` to print the comment without posting (use it first on any live repo).
Zero findings renders a short "no issues found" comment; a `missing-docs-only` run with zero
findings posts nothing. If the marker `<!-- review-doc-pr:v1 -->` is already on the PR, the run
skips: it is a duplicate invocation, not an update.

## Error handling

- Source repo not found (non-`self` profile): accuracy degrades to `unverifiable`.
- Style guide missing on the base branch: use the bundled copy and say so in the comment.
- Link-check network failure: no finding for that URL; never a false "broken".
- Comment over the size cap: shorten suggestions and state what was shortened.
