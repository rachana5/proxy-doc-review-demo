---
name: review-doc-pr
description: Runs once per pull request and posts one advisory docs review comment. Scoped to what the PR changes: reviews the changed docs and every other page affected by the implementation change (accuracy, style, reference, clarity, completeness), and, when user-facing code changed, checks whether docs are missing and drafts them. Read-only, never applies fixes, never blocks merge. Product comes from a profile (`--profile proxy`). Invoke non-interactively as `/review-doc-pr <pr-number> --profile proxy`.
allowed-tools: "Read Grep Glob Bash(python3:*) Bash(git:*) Bash(gh:*)"
---

# review-doc-pr

Product settings (docs location, doc engine, style guide, which code counts as user-facing,
bot PRs to skip) come from `profiles/<name>.json`; the review layers are the same for every product.

**Scope rule:** every layer is scoped to the behavior this PR changes, never to a whole file. A
page is in scope only for claims about the changed behavior, whether or not the PR edits that
page. Anything else on the page is out of scope, even if it is wrong.

Read-only and advisory: never applies fixes, never edits the PR, never blocks merge.
Fires once per PR; the comment carries a marker so a CI retry skips instead of
duplicating (no edit-in-place).

## Running the scripts

Scripts live in `${CLAUDE_SKILL_DIR}/scripts/` and run as
`PYTHONPATH="${CLAUDE_SKILL_DIR}" python3 -m scripts.<name>`. References are in
`${CLAUDE_SKILL_DIR}/references/`: `finding-schema.md`, one checklist per layer
(`accuracy-checklist.md`, `style-checklist.md`, `reference-checklist.md`, `clarity-checklist.md`,
`completeness-checklist.md`), `missing-docs-checklist.md`, `affected-docs-checklist.md`, and the
Proxy style guide fallback `proxy-style-guide.md`. The comment template is
`${CLAUDE_SKILL_DIR}/templates/pr-comment.md.tmpl`. Helpers the steps below use implicitly:
`profile.py`, `_finding.py`, `_gh.py`, `_git.py`, `run_style_lint.py` (only for profiles that
configure a linter).

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
| `full-review` | Step 2b, Step 3 (all layers), and Step 3b if `run_missing_docs` | one comment |
| `missing-docs-only` | Step 2b, Step 3b, and the accuracy layer on affected pages only (code changed, no docs touched: a page that still states the old default is the typical finding) | a comment only if a finding exists |
| `silent` | nothing | nothing |

## Step 2b: Find the change set and the affected pages

Skip when `action` is `silent`. Otherwise:

1. **Change set.** List the terms this PR changes: from the code diff of each `user_facing_code`
   file, every option, field, flag, label, middleware or provider name that is new, renamed, removed,
   or has a changed default or behavior. For a docs-only PR (no code diff), use the options and
   claims in the changed doc lines instead. Write them as one comma-separated list.
2. **Search the whole docs tree** for those terms. The profile's `doc_targets` seed the ranking;
   the search is what finds pages the map does not know:

```bash
PYTHONPATH="${CLAUDE_SKILL_DIR}" python3 -m scripts.find_affected_docs --profile proxy \
  --repo-root <root> --terms "<term1>,<term2>" --classify classify.json > affected.json
```

3. Read each candidate page in `affected.json` and apply `references/affected-docs-checklist.md`.
   Pages with `in_pr: false` are the ones the PR forgot: a reference table, a sibling guide, a
   migration note. Findings on pages the PR does not edit are always `suggestion` (Step 4).

## Step 3: Review layers

Every layer is scoped to the change set, not the file. "Changed lines" means the PR's changed
lines (`changed-lines.json`); "affected pages" means `affected.json`.

| Layer | Scope |
|---|---|
| Accuracy | Changed lines: every claim. Everywhere else (rest of a changed page, affected pages): only claims about the change set, including a sentence far from the edit that the change now contradicts. Evidence is the PR's code diff first, then surrounding code (struct, defaults, tests) |
| Reference: mechanical (`check_links.py`) and judgment | Changed lines. On affected pages: only a link or anchor this PR broke (a renamed or removed heading or page); mark it `affected: true` |
| Style (`references/style-checklist.md`, the Proxy style guide) | Changed lines only |
| Clarity | Changed lines only |
| Completeness | The change set: is it documented everywhere it should be (every format, reference page, migration note)? Not "is this page thorough". Always `suggestion`, `auto_fixable: false` |

Each layer writes `<layer>.json` in the shape of `references/finding-schema.md`. If
`run_style_lint.py` ran, unwrap its dict output first; for Proxy no linter runs, so style is
agent-only and the comment says so. Write `[]` for a layer with no findings.

Reference layer, mechanical part. Proxy docs are MkDocs, so pass the engine and docs root; the
default mode would false-flag every directory-style link and does not check anchors:

```bash
PYTHONPATH="${CLAUDE_SKILL_DIR}" python3 -m scripts.check_links --repo-root <root> \
  --engine mkdocs --docs-root docs/content <changed doc files> > reference.json
```

Run it on the changed doc files, then on affected pages and keep only findings whose broken
target this PR changed (set `affected: true`). Append your judgment findings (missing links on
changed lines) to that list. Validate every file:

```bash
PYTHONPATH="${CLAUDE_SKILL_DIR}" python3 -m scripts._finding <layer>.json
```

A finding that fails validation: re-prompt with the validator error, max 3 attempts, then
replace it with an `unverifiable` finding at the same location. Never fail the run over one finding.

## Step 3b: Missing-docs check (user-facing code changed)

Follow `references/missing-docs-checklist.md` for each `user_facing_code` entry, using
`affected.json` to see what the docs already say anywhere in the tree. Write the results as
`completeness` findings (merge into `completeness.json` when both exist).
If `generated_touched` is non-empty, report it as the top style finding.

## Step 4: Cap severity outside the diff

Findings whose line is outside the PR's changed lines, including every finding on a page the PR
does not edit, become `suggestion`. Nothing is dropped.
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
  --changed-lines changed-lines.json --template templates/pr-comment.md.tmpl \
  --profile proxy --classify classify.json
```

`--profile` applies the profile's `drop_outside_diff_layers` (Proxy: `reference`): a dead link on a
line the PR did not change is not shown, unless the finding is `affected: true`. With 8 or more
suggestions, related ones are grouped into one collapsed row (same `group` value, or all link
findings); blocking findings are never grouped and every member stays readable inside the group. `--classify` applies the silence rules from Step 2: `silent`,
or `missing-docs-only` with zero findings, posts nothing and exits 0 (no hand-written files needed).
Add `--dry-run` to print the comment without posting (use it first on any live repo). A `full-review`
with zero findings renders a short "no issues found" comment. If the marker
`<!-- review-doc-pr:v1 -->` is already on the PR, the run skips: it is a duplicate invocation,
not an update.

## Error handling

- Source repo not found (non-`self` profile): accuracy degrades to `unverifiable`.
- Style guide missing on the base branch: use the bundled copy and say so in the comment.
- Link-check network failure: no finding for that URL; never a false "broken".
- Comment over the size cap: shorten suggestions and state what was shortened.
