# proxy-doc-review-demo

A demo of an automated, advisory docs review for [Traefik Proxy](https://github.com/traefik/traefik) pull requests. It is a throwaway proof of concept, tested only in a personal fork. It is not proposed upstream and nothing here runs on `traefik/traefik`.

## What it does

When a PR opens, the check posts one comment and never edits the PR or blocks the merge.

| The PR contains | What runs | What is posted |
|---|---|---|
| Doc changes | Review of the changed lines plus any claim about the changed behavior, on any page (accuracy, style, reference, clarity, completeness). Missing-docs check too if user-facing code changed. | One comment |
| User-facing code, no docs | Missing-docs check, plus a search of all docs for pages the change makes wrong or incomplete | A comment only if there is a finding |
| Neither (tests, refactors) | Nothing | Nothing |

Design: [docs/proxy-doc-review-design.md](docs/proxy-doc-review-design.md). Style guide used by the style layer: [docs/proxy-style-guide.md](docs/proxy-style-guide.md). Flow diagram: [docs/2026-10-08-proxy-doc-review-workflow.png](docs/2026-10-08-proxy-doc-review-workflow.png).

## What a PR looks like

Two seeded PRs, run against the real `traefik/traefik` Retry middleware. The rendered comments are in `examples/run/`:

1. **Docs PR with planted mistakes** ([comment](examples/run/docs-mistakes/comment.md)): a wrong default (the doc says 1MB, the code says 2 MB at `pkg/config/dynamic/middlewares.go:17`), a broken link, and four style violations. Result: 2 blocking, 4 suggestions. The existing `[here]` links elsewhere on the page are not flagged because style only reads changed lines.
2. **Code PR with no docs** ([comment](examples/run/code-no-docs/comment.md)): a new `maxBackoff` option. Result: one suggestion with a ready-to-paste table row, where to add the example lines, and a warning that the diff does not wire the option into `retry.go` yet.

These two runs were produced by Claude Code following `skill/review-doc-pr/SKILL.md` locally in dry-run mode (the agent layers are LLM judgment; the classifier, link checker, aggregation and rendering are scripts). They were not run in CI.

## Replay on real merged PRs

Six real `traefik/traefik` PRs were replayed locally (branches rebuilt from each PR's base, the PR applied, one reviewer agent per PR, dry run). Rendered comments are in `examples/replay/pr-<number>/comment.md`.

| PR | What it is | Result |
|---|---|---|
| 13955 | Maintainer docs clarification | 1 low-confidence suggestion |
| 13925 | External contributor, dead-anchor fix | No issues found (re-run after the confirmations-are-not-findings rule) |
| 13873 | External feature with docs | 2 suggestions |
| 13882 | Feature with docs (double wildcard matchers) | 4 suggestions, no blocking |
| 13882 with docs removed | Tests the missing-docs check | 4 findings, 3 of the 4 pages the real PR updated; missed the migration note |
| 13939 | External code-only bug fix | Silent, as intended |

What the replay found and fixed in this demo:

- The code-to-doc map missed router rule matchers and ACME. Both are now in `profiles/proxy.json`.
- The link checker gave 27 false "broken link" results across the Proxy docs, because MkDocs directory-style URLs are not file paths. It now has a MkDocs mode (`--engine mkdocs`) that resolves them like the built site, resolves `include-markdown` banners, and validates `#anchors`. On the pre-fix pages of PR 13925 it reports exactly the 4 dead anchors that PR fixed. On all 169 current Proxy docs pages it reports 11 findings, which are real dead anchors (a heading like `users & usersFile` slugs to `users-usersfile`, but the link has a double hyphen).
- Dead links on lines a PR did not change are no longer listed (`drop_outside_diff_layers` in the profile).
- Collapsed headlines use only the first sentence of the reasoning; the full text is in the body.
- Zero-finding code-only PRs post nothing, handled by `--classify`, not by hand.
- The style checklist no longer contradicts the style guide on Title Case headings; the completeness, accuracy, and reference checklists no longer carry Hub-specific paths.

Known weak spots: the agent layers still produce occasional low-confidence nits (0.35 to 0.5), and nothing here has a measured false-positive rate. Anchor slugs assume the default MkDocs `toc` extension, which is what `docs/mkdocs.yml` configures.

## What changed from the Hub skill

This is a copy of the Hub per-PR review skill with a product **profile** added, so the review layers stay product-neutral.

- `skill/review-doc-pr/profiles/proxy.json`: docs path, MkDocs, style guide location, bot PRs to skip, generated files, and the map from code areas to doc pages. `hub.json` is an illustrative second profile.
- `scripts/profile.py`, `scripts/missing_docs.py`, profile-driven `scripts/pr_filter.py`: new.
- `references/missing-docs-checklist.md`, a Proxy `references/style-checklist.md`, and the bundled style guide: new.
- `templates/pr-comment.md.tmpl`: collapsible suggestions, a "drafts, verify them" note.
- `check_links.py`: shows repo-relative paths, so no runner paths end up in a public comment.

## Try it

```bash
cd skill/review-doc-pr
PYTHONPATH=. python3 -m pytest scripts/tests -q          # 209 tests

# Classify a PR's files against the Proxy profile
git diff --name-only origin/master...<branch> | PYTHONPATH=. python3 -m scripts.missing_docs --profile proxy
```

To see the comment on a real PR, use a fork of `traefik/traefik`, copy `skill/review-doc-pr` to `.claude/skills/review-doc-pr`, and run `/review-doc-pr <pr-number> --profile proxy` in Claude Code with `--dry-run` first. `examples/workflows/doc-review.yml` is an untested CI template for the fork.

## Not done in this demo

Replay on 5 to 10 merged PRs, a measured false-positive bar, fork-PR security, the Docusaurus profile, size cap enforcement, and a tested CI workflow. See the open items in the design doc.
