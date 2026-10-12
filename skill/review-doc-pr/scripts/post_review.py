"""post_review.py — renders review-doc-pr's aggregated findings as one PR
comment and posts it, unless one from a previous run of this same PR state
is already there.

This is the only network-writing step in review-doc-pr, and the only place
the plan's "fires once per PR" contract and the marker-based idempotency
check actually meet: a marker match means this workflow got invoked twice
for the same PR (e.g. a CI retry after an infra blip), not a legitimate
update, so the right behavior is to skip, not to edit the existing comment
in place. See docs/superpowers/plans/2026-09-17-per-pr-review-skill-plan.md
(in the automation workspace)'s "New work required" item 2 and the note
under SKILL.md's Step 6 for the full reasoning.

Reuses aggregate.render_report() (content-reviewer's engine, duplicated
byte-for-byte into this skill — kept in sync by
scripts/tests/test_content_reviewer_duplication_sync.py in the
ai-doc-content-reviewer source repo, not re-verified from inside hub-doc,
since that test file is deliberately not copied here — see SKILL.md's
"Bundled resources" for why) for the
non-empty case; the empty-findings case is this module's own special case,
since the mustache-ish template has no conditionals to express "no
findings" without producing an awkward "0 blocking · 0 suggestions" body.
"""
from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path

from scripts import _gh, aggregate, changed_lines

MARKER = "<!-- review-doc-pr:v1 -->"

_EMPTY_BODY = f"""## Docs review: no issues found

Automated review against the code and the style guide found nothing to flag. Nothing here blocks merge. This PR goes through its normal review.

{MARKER}
"""


def cap_severity_outside_diff(
    findings: list[dict], changed_ranges: dict[str, list[list[int]]],
) -> list[dict]:
    """Returns a new list, findings unchanged except `severity` forced to
    "suggestion" for any finding whose (file, line) falls outside the PR's
    own changed-line ranges.

    `blocking` is reserved for findings inside the PR's own changed lines
    (see the plan's "Severity cap for out-of-diff findings" section) — the
    whole-file accuracy/reference scan's value is surfacing drift the PR
    happens to touch, not making an unrelated pre-existing issue this PR's
    problem to fix. This cap applies uniformly to every finding regardless
    of layer -- nothing needs to check `layer`/`layers` to tell the
    difference. That includes style/clarity: run_style_lint.py actually
    scans the whole file (vale/alex have no notion of "just these lines"),
    so a style finding CAN land outside the diff -- it still gets capped
    to `suggestion` by this same generic check, it isn't exempted.

    Must run before render_report() is called (whether that's from this
    module or from an `aggregate` CLI invocation upstream of it) --
    render_report()'s blocking_count/suggestion_count are computed
    directly from whatever `severity` is on each finding at that point.
    """
    capped = []
    for finding in findings:
        f = dict(finding)
        ranges = [tuple(r) for r in changed_ranges.get(f["file"], [])]
        if not changed_lines.line_in_ranges(f["line"], ranges):
            f["severity"] = "suggestion"
        capped.append(f)
    return capped


def drop_outside_diff(
    findings: list[dict], changed_ranges: dict[str, list[list[int]]], layers: list[str],
) -> list[dict]:
    """Remove findings from `layers` whose line is outside the PR's changed
    lines (a finding merged from several layers is kept if any layer is not
    droppable). Used by profiles whose reference layer scans whole files: an
    old dead link the PR did not touch is not this PR's problem, and listing
    it makes the comment noisy."""
    if not layers:
        return findings
    kept = []
    for f in findings:
        fl = f.get("layers", [f["layer"]])
        ranges = [tuple(r) for r in changed_ranges.get(f["file"], [])]
        outside = not changed_lines.line_in_ranges(f["line"], ranges)
        if outside and all(l in layers for l in fl):
            continue
        kept.append(f)
    return kept


COMMENT_SIZE_CAP = 60_000  # GitHub's hard limit is 65,536 characters per comment
_FIX_CAP_ON_SHRINK = 500

_SEVERITY_MARK = {"blocking": "\U0001F534", "suggestion": "\U0001F7E1"}


def _sentences(text: str) -> tuple[str, str]:
    """(first sentence, the rest) of a whitespace-normalized text."""
    text = " ".join(str(text).split())
    m = re.match(r"(.+?[.!?])(?:\s+(.*))?$", text)
    return (m.group(1), m.group(2) or "") if m else (text, "")


def _html_inline(text: str) -> str:
    """Markdown is not rendered inside <summary>, so turn `code` into <code>."""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", text)


def _short_path(path: str) -> str:
    return "/".join(path.split("/")[-2:])


def _is_simple_edit(f: dict) -> bool:
    quote, fix = f["quote"], f["suggested_fix"]
    return (
        f["layer"] != "completeness"
        and "\n" not in quote and "\n" not in fix
        and not fix.startswith("(") and len(quote) < 400 and len(fix) < 400
    )


_LAYER_LABEL = {
    "accuracy": "Accuracy", "style": "Style guide", "reference": "Links and references",
    "clarity": "Clarity", "completeness": "Missing docs",
}


def render_finding(f: dict, fix_cap: int | None = None) -> str:
    """Collapsed row: marker, file:line, the rule that is not being followed.
    Expanded body: what is wrong, then the suggested fix. Nothing is cut off:
    the full reasoning is always in the body."""
    rule = f.get("rule") or _LAYER_LABEL.get(f["layer"], f["layer"].title())
    mark = _SEVERITY_MARK.get(f["severity"], "")
    summary = f'{mark} <code>{_short_path(f["file"])}:{f["line"]}</code> &nbsp;·&nbsp; {_html_inline(rule)}'
    quote, fix = f["quote"].strip(), f["suggested_fix"].strip()
    if fix_cap is not None and len(fix) > fix_cap:
        fix = fix[:fix_cap].rstrip() + "\n\n_(shortened to fit the comment size limit)_"
    parts = [f"<details>\n<summary>{summary}</summary>\n"]
    parts.append(f"**What's wrong:** {' '.join(str(f.get('reasoning', '')).split())}\n")
    if _is_simple_edit(f):
        parts.append("**Suggested fix:**\n")
        parts.append(f"```diff\n- {quote}\n+ {fix}\n```\n")
    elif f["layer"] == "completeness":
        parts.append(f"**Code change:** {quote}\n")
        parts.append("**Suggested fix:**\n")
        parts.append(f"{fix}\n")
    else:
        parts.append("\n".join("> " + line for line in quote.splitlines()) + "\n")
        parts.append("**Suggested fix:**\n")
        parts.append(f"{fix}\n")
    parts.append("</details>\n")
    return "\n".join(parts)


def render_findings_block(findings: list[dict]) -> str:
    """Blocking first, then suggestions; within each, by file and line. If the
    result would exceed the size cap, shorten the longest suggested fixes."""
    ordered = sorted(findings, key=lambda f: (f["severity"] != "blocking", f["file"], f["line"]))
    block = "\n".join(render_finding(f) for f in ordered)
    if len(block) > COMMENT_SIZE_CAP:
        block = "\n".join(render_finding(f, fix_cap=_FIX_CAP_ON_SHRINK) for f in ordered)
        block += "\n_Some suggested text was shortened to fit the comment size limit._\n"
    return block


def render_comment(findings: list[dict], template_text: str, marker: str = MARKER) -> str:
    """The zero-findings special case the mustache-ish template can't
    express on its own (see module docstring); anything non-empty just
    delegates to the already-reused aggregate.render_report().

    `marker` defaults to MARKER; both _EMPTY_BODY and the template file
    embed MARKER as a literal string (there's no {{marker}} placeholder
    to substitute), so a non-default marker is swapped in with a targeted
    string replace afterward. Without this, a caller passing --marker to
    bump the sentinel would change what has_existing_comment searches for
    without changing what actually gets posted -- the idempotency check
    and the posted body silently disagreeing on the marker."""
    if not findings:
        body = _EMPTY_BODY
    elif "{{findings_block}}" in template_text:
        # Header/footer come from the template; the findings are laid out in
        # Python (conditional layout the mustache-ish renderer can't express).
        # Fill the block last so finding text is never scanned for placeholders.
        body = aggregate.render_report(findings, template_text)
        body = body.replace("{{findings_block}}", render_findings_block(findings))
    else:
        body = aggregate.render_report(findings, template_text)
    body = re.sub(r"\b1 suggestions\b", "1 suggestion", body)
    if marker != MARKER:
        body = body.replace(MARKER, marker)
    return body


def has_existing_comment(repo: str, pr: str, marker: str = MARKER) -> bool:
    """True if a PR comment containing `marker` already exists.

    Uses `gh pr view --json comments`, not `gh api .../comments
    --paginate` -- the latter prints one JSON array per page when a PR has
    enough comments to paginate, which is NOT valid single-document JSON
    for json.loads to parse. `gh pr view --json` returns one object
    regardless of how many comments there are.
    """
    raw = _gh.run(["pr", "view", pr, "--repo", repo, "--json", "comments"])
    data = json.loads(raw)
    return any(marker in c.get("body", "") for c in data.get("comments", []))


def post_comment(repo: str, pr: str, body: str) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(body)
        body_path = f.name
    try:
        _gh.run(["pr", "comment", pr, "--repo", repo, "--body-file", body_path])
    finally:
        Path(body_path).unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render and post review-doc-pr's findings as one PR comment.")
    parser.add_argument("--repo", required=True, help="owner/repo, e.g. traefik/hub-doc")
    parser.add_argument("--pr", required=True, help="PR number")
    parser.add_argument("--findings", required=True, help="path to aggregate.py's merged findings JSON")
    parser.add_argument("--changed-lines", required=True, help="path to scripts.changed_lines's output JSON")
    parser.add_argument("--template", required=True, help="path to templates/pr-comment.md.tmpl")
    parser.add_argument("--marker", default=MARKER)
    parser.add_argument("--profile", help="product profile; its drop_outside_diff_layers removes out-of-diff findings of those layers")
    parser.add_argument("--classify", help="classify.json from scripts.missing_docs; decides whether any comment is posted at all")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="print what would be posted instead of calling gh — no marker check either, "
             "since a dry run isn't the real invocation this skill fires once per PR for.",
    )
    args = parser.parse_args(argv)

    action = json.loads(Path(args.classify).read_text())["action"] if args.classify else None
    findings = json.loads(Path(args.findings).read_text())
    changed_ranges = json.loads(Path(args.changed_lines).read_text())
    if args.profile:
        from scripts import profile as profile_mod
        findings = drop_outside_diff(
            findings, changed_ranges, profile_mod.load(args.profile).get("drop_outside_diff_layers", []))
    findings = cap_severity_outside_diff(findings, changed_ranges)

    # Silence rules: nothing to review, or a code-only PR with no docs gap found.
    if action == "silent" or (action == "missing-docs-only" and not findings):
        print(f"[post_review] action={action} with {len(findings)} finding(s): no comment posted.")
        return 0
    template_text = Path(args.template).read_text()
    body = render_comment(findings, template_text, args.marker)

    if args.dry_run:
        print(body)
        return 0

    if has_existing_comment(args.repo, args.pr, args.marker):
        print(f"[post_review] a comment with marker {args.marker!r} already exists on "
              f"{args.repo}#{args.pr} — skipping (this run is a duplicate invocation, not an update).")
        return 0

    post_comment(args.repo, args.pr, body)
    print(f"[post_review] posted review comment to {args.repo}#{args.pr}.")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
