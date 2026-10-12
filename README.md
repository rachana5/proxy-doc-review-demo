# proxy-doc-review-demo

A demo of an automated, advisory docs review for [Traefik Proxy](https://github.com/traefik/traefik) pull requests. It is a throwaway proof of concept, tested only in a personal fork. It is not proposed upstream and nothing here runs on `traefik/traefik`.

## What it does

When a PR opens, the check posts one comment and never edits the PR or blocks the merge.

| The PR contains | What runs | What is posted |
|---|---|---|
| Doc changes | Full review (accuracy, style, reference, clarity, completeness). Missing-docs check too if user-facing code changed. | One comment |
| User-facing code, no docs | Missing-docs check only | A comment only if docs are needed |
| Neither (tests, refactors) | Nothing | Nothing |

Design: [docs/proxy-doc-review-design.md](docs/proxy-doc-review-design.md). Style guide used by the style layer: [docs/proxy-style-guide.md](docs/proxy-style-guide.md). Flow diagram: [docs/2026-10-08-proxy-doc-review-workflow.png](docs/2026-10-08-proxy-doc-review-workflow.png).

## What a PR looks like

Two seeded PRs, run against the real `traefik/traefik` Retry middleware. The rendered comments are in `examples/run/`:

1. **Docs PR with planted mistakes** ([comment](examples/run/docs-mistakes/comment.md)): a wrong default (the doc says 1MB, the code says 2 MB at `pkg/config/dynamic/middlewares.go:17`), a broken link, and four style violations. Result: 2 blocking, 4 suggestions. The existing `[here]` links elsewhere on the page are not flagged because style only reads changed lines.
2. **Code PR with no docs** ([comment](examples/run/code-no-docs/comment.md)): a new `maxBackoff` option. Result: one suggestion with a ready-to-paste table row, where to add the example lines, and a warning that the diff does not wire the option into `retry.go` yet.

These two runs were produced by Claude Code following `skill/review-doc-pr/SKILL.md` locally in dry-run mode (the agent layers are LLM judgment; the classifier, link checker, aggregation and rendering are scripts). They were not run in CI.

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
PYTHONPATH=. python3 -m pytest scripts/tests -q          # 178 tests

# Classify a PR's files against the Proxy profile
git diff --name-only origin/master...<branch> | PYTHONPATH=. python3 -m scripts.missing_docs --profile proxy
```

To see the comment on a real PR, use a fork of `traefik/traefik`, copy `skill/review-doc-pr` to `.claude/skills/review-doc-pr`, and run `/review-doc-pr <pr-number> --profile proxy` in Claude Code with `--dry-run` first. `examples/workflows/doc-review.yml` is an untested CI template for the fork.

## Not done in this demo

Replay on 5 to 10 merged PRs, a measured false-positive bar, fork-PR security, the Docusaurus profile, size cap enforcement, and a tested CI workflow. See the open items in the design doc.
