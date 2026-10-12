from __future__ import annotations

import json

from scripts import post_review


def _finding(file="docs/foo.md", line=10, severity="blocking", **overrides):
    base = {
        "layer": "accuracy", "layers": ["accuracy"], "file": file, "line": line,
        "quote": "some text", "reasoning": "why", "suggested_fix": "fix",
        "severity": severity, "confidence": 0.9, "auto_fixable": True,
    }
    base.update(overrides)
    return base


def test_cap_severity_outside_diff_downgrades_findings_outside_changed_ranges():
    findings = [_finding(line=50, severity="blocking")]
    changed_ranges = {"docs/foo.md": [[1, 5]]}
    capped = post_review.cap_severity_outside_diff(findings, changed_ranges)
    assert capped[0]["severity"] == "suggestion"


def test_cap_severity_outside_diff_leaves_in_diff_findings_alone():
    findings = [_finding(line=3, severity="blocking")]
    changed_ranges = {"docs/foo.md": [[1, 5]]}
    capped = post_review.cap_severity_outside_diff(findings, changed_ranges)
    assert capped[0]["severity"] == "blocking"


def test_cap_severity_outside_diff_treats_missing_file_as_fully_out_of_diff():
    findings = [_finding(file="docs/untouched.md", line=1, severity="blocking")]
    changed_ranges = {"docs/foo.md": [[1, 5]]}
    capped = post_review.cap_severity_outside_diff(findings, changed_ranges)
    assert capped[0]["severity"] == "suggestion"


def test_cap_severity_outside_diff_does_not_mutate_input():
    findings = [_finding(line=50, severity="blocking")]
    changed_ranges = {"docs/foo.md": [[1, 5]]}
    post_review.cap_severity_outside_diff(findings, changed_ranges)
    assert findings[0]["severity"] == "blocking"


def test_render_comment_empty_findings_uses_friendly_special_case():
    body = post_review.render_comment([], "irrelevant template text")
    assert "no issues found" in body.lower()
    assert post_review.MARKER in body
    assert "blocking" not in body.lower().split("no issues found")[0]


def test_render_comment_nonempty_delegates_to_aggregate_render_report():
    template = "## {{blocking_count}} blocking\n{{#findings}}{{file}}:{{line}}\n{{/findings}}"
    findings = [_finding(file="docs/a.md", line=1, severity="blocking", layers=["accuracy"])]
    body = post_review.render_comment(findings, template)
    assert "1 blocking" in body
    assert "docs/a.md:1" in body


def test_render_comment_embeds_a_custom_marker_on_empty_findings():
    # --marker previously only changed what has_existing_comment searches
    # for, never what actually got posted -- a marker bump would silently
    # keep embedding the old sentinel, breaking "fires once per PR" the
    # moment the marker is ever changed.
    body = post_review.render_comment([], "irrelevant", marker="<!-- review-doc-pr:v2 -->")
    assert "<!-- review-doc-pr:v2 -->" in body
    assert post_review.MARKER not in body


def test_render_comment_embeds_a_custom_marker_on_nonempty_findings():
    template = f"## report\n{{{{#findings}}}}{{{{file}}}}{{{{/findings}}}}\n{post_review.MARKER}\n"
    findings = [_finding(file="docs/a.md", line=1, severity="blocking", layers=["accuracy"])]
    body = post_review.render_comment(findings, template, marker="<!-- review-doc-pr:v2 -->")
    assert "<!-- review-doc-pr:v2 -->" in body
    assert post_review.MARKER not in body


def test_has_existing_comment_true_when_marker_present(monkeypatch):
    monkeypatch.setattr(
        post_review._gh, "run",
        lambda args: json.dumps({"comments": [{"body": f"hello {post_review.MARKER}"}]}),
    )
    assert post_review.has_existing_comment("owner/repo", "42") is True


def test_has_existing_comment_false_when_absent(monkeypatch):
    monkeypatch.setattr(
        post_review._gh, "run",
        lambda args: json.dumps({"comments": [{"body": "unrelated comment"}]}),
    )
    assert post_review.has_existing_comment("owner/repo", "42") is False


def test_has_existing_comment_false_when_no_comments_at_all(monkeypatch):
    monkeypatch.setattr(post_review._gh, "run", lambda args: json.dumps({"comments": []}))
    assert post_review.has_existing_comment("owner/repo", "42") is False


def test_has_existing_comment_uses_pr_view_json_not_paginated_api(monkeypatch):
    calls = []

    def _run(args):
        calls.append(args)
        return json.dumps({"comments": []})

    monkeypatch.setattr(post_review._gh, "run", _run)
    post_review.has_existing_comment("owner/repo", "42")
    assert calls == [["pr", "view", "42", "--repo", "owner/repo", "--json", "comments"]]


def test_post_comment_calls_gh_pr_comment_with_a_body_file(monkeypatch, tmp_path):
    calls = []
    written_bodies = []

    def _run(args):
        calls.append(args)
        # simulate reading the --body-file argument's contents before cleanup
        body_file_path = args[args.index("--body-file") + 1]
        written_bodies.append(open(body_file_path).read())
        return ""

    monkeypatch.setattr(post_review._gh, "run", _run)
    post_review.post_comment("owner/repo", "42", "the rendered body")
    assert calls[0][:4] == ["pr", "comment", "42", "--repo"]
    assert written_bodies == ["the rendered body"]


def test_main_skips_posting_when_marker_already_present(monkeypatch, tmp_path, capsys):
    findings_path = tmp_path / "merged.json"
    findings_path.write_text(json.dumps([]))
    changed_lines_path = tmp_path / "changed.json"
    changed_lines_path.write_text(json.dumps({}))
    template_path = tmp_path / "template.md.tmpl"
    template_path.write_text("irrelevant")

    monkeypatch.setattr(post_review, "has_existing_comment", lambda repo, pr, marker=post_review.MARKER: True)

    posted = []
    monkeypatch.setattr(post_review, "post_comment", lambda repo, pr, body: posted.append((repo, pr, body)))

    exit_code = post_review.main([
        "--repo", "owner/repo", "--pr", "42",
        "--findings", str(findings_path),
        "--changed-lines", str(changed_lines_path),
        "--template", str(template_path),
    ])
    assert exit_code == 0
    assert posted == []
    assert "skipping" in capsys.readouterr().out


def test_main_posts_when_no_existing_comment(monkeypatch, tmp_path):
    findings_path = tmp_path / "merged.json"
    findings_path.write_text(json.dumps([]))
    changed_lines_path = tmp_path / "changed.json"
    changed_lines_path.write_text(json.dumps({}))
    template_path = tmp_path / "template.md.tmpl"
    template_path.write_text("irrelevant")

    monkeypatch.setattr(post_review, "has_existing_comment", lambda repo, pr, marker=post_review.MARKER: False)

    posted = []
    monkeypatch.setattr(post_review, "post_comment", lambda repo, pr, body: posted.append((repo, pr, body)))

    exit_code = post_review.main([
        "--repo", "owner/repo", "--pr", "42",
        "--findings", str(findings_path),
        "--changed-lines", str(changed_lines_path),
        "--template", str(template_path),
    ])
    assert exit_code == 0
    assert len(posted) == 1
    assert posted[0][0] == "owner/repo"
    assert posted[0][1] == "42"
    assert "no issues found" in posted[0][2].lower()


def test_main_dry_run_prints_without_checking_marker_or_posting(monkeypatch, tmp_path, capsys):
    findings_path = tmp_path / "merged.json"
    findings_path.write_text(json.dumps([]))
    changed_lines_path = tmp_path / "changed.json"
    changed_lines_path.write_text(json.dumps({}))
    template_path = tmp_path / "template.md.tmpl"
    template_path.write_text("irrelevant")

    def _boom(*a, **k):
        raise AssertionError("dry-run must not check for an existing comment")

    monkeypatch.setattr(post_review, "has_existing_comment", _boom)
    monkeypatch.setattr(post_review, "post_comment", lambda *a, **k: (_ for _ in ()).throw(AssertionError("dry-run must not post")))

    exit_code = post_review.main([
        "--repo", "owner/repo", "--pr", "42",
        "--findings", str(findings_path),
        "--changed-lines", str(changed_lines_path),
        "--template", str(template_path),
        "--dry-run",
    ])
    assert exit_code == 0
    assert "no issues found" in capsys.readouterr().out.lower()


def test_main_applies_severity_cap_before_rendering(tmp_path, capsys):
    # line 99 is outside the [1, 5] changed range -- the finding starts
    # "blocking" but must render as capped to "suggestion" before the
    # template's counts are computed.
    findings_path = tmp_path / "merged.json"
    findings_path.write_text(json.dumps([_finding(file="docs/a.md", line=99, severity="blocking")]))
    changed_lines_path = tmp_path / "changed.json"
    changed_lines_path.write_text(json.dumps({"docs/a.md": [[1, 5]]}))
    template_path = tmp_path / "template.md.tmpl"
    template_path.write_text(
        "{{blocking_count}} blocking, {{suggestion_count}} suggestions"
    )

    exit_code = post_review.main([
        "--repo", "owner/repo", "--pr", "42",
        "--findings", str(findings_path),
        "--changed-lines", str(changed_lines_path),
        "--template", str(template_path),
        "--dry-run",
    ])
    assert exit_code == 0
    assert "0 blocking, 1 suggestion" in capsys.readouterr().out


def test_drop_outside_diff_removes_only_listed_layers_outside_the_diff():
    from scripts import post_review as pr
    ranges = {"a.md": [[10, 12]]}
    fs = [
        {"layer": "reference", "file": "a.md", "line": 99},   # outside, droppable
        {"layer": "reference", "file": "a.md", "line": 11},   # inside, kept
        {"layer": "accuracy", "file": "a.md", "line": 99},    # outside, other layer, kept
        {"layer": "reference", "layers": ["reference", "style"], "file": "a.md", "line": 99},  # mixed, kept
    ]
    kept = pr.drop_outside_diff(fs, ranges, ["reference"])
    assert [(f["layer"], f["line"]) for f in kept] == [("reference", 11), ("accuracy", 99), ("reference", 99)]


def test_classify_silent_posts_nothing(tmp_path, capsys):
    import json
    from scripts import post_review as pr
    for name, data in {"f.json": [], "c.json": {}, "k.json": {"action": "missing-docs-only"}}.items():
        (tmp_path / name).write_text(json.dumps(data))
    tmpl = tmp_path / "t.tmpl"; tmpl.write_text("x")
    rc = pr.main(["--repo", "o/r", "--pr", "1", "--findings", str(tmp_path / "f.json"),
                  "--changed-lines", str(tmp_path / "c.json"), "--template", str(tmpl),
                  "--classify", str(tmp_path / "k.json"), "--dry-run"])
    assert rc == 0 and "no comment posted" in capsys.readouterr().out


# --- new comment layout ----------------------------------------------------
def _f(layer, sev, line, quote="old text", fix="new text", reasoning="Rule one. Extra evidence."):
    return {"layer": layer, "file": "docs/content/a/b/page.md", "line": line, "quote": quote,
            "reasoning": reasoning, "suggested_fix": fix, "severity": sev,
            "confidence": 0.7, "auto_fixable": False}


def test_blocking_findings_come_first_then_by_line():
    from scripts import post_review as pr
    block = pr.render_findings_block([_f("style", "suggestion", 3), _f("accuracy", "blocking", 90), _f("style", "suggestion", 1)])
    assert block.index(":90") < block.index(":1<") < block.index(":3<")


def test_simple_edit_renders_as_diff_and_has_no_headings_or_tables():
    from scripts import post_review as pr
    out = pr.render_findings_block([_f("style", "suggestion", 7)])
    assert "```diff\n- old text\n+ new text\n```" in out
    assert "\n#" not in out and "|---" not in out


def test_summary_uses_html_code_not_markdown_backticks():
    from scripts import post_review as pr
    out = pr.render_finding(_f("style", "suggestion", 7, reasoning="Use `uses` not leverages."))
    summary = out.split("<summary>")[1].split("</summary>")[0]
    assert "`" not in summary and "<code>uses</code>" in summary


def test_multiline_fix_is_not_forced_into_a_diff():
    from scripts import post_review as pr
    out = pr.render_finding(_f("completeness", "suggestion", 1, quote="pkg/x.go: new option", fix="Add:\n\n```markdown\n| a |\n```"))
    assert "```diff" not in out and "> pkg/x.go: new option" in out and "```markdown" in out


def test_oversized_comment_shortens_fixes_and_says_so():
    from scripts import post_review as pr
    big = [_f("completeness", "suggestion", i, fix="x" * 3000) for i in range(30)]
    out = pr.render_findings_block(big)
    assert len(out) < pr.COMMENT_SIZE_CAP + 2000 and "shortened" in out


def test_singular_suggestion_count():
    from scripts import post_review as pr
    tmpl = "## Docs review: {{blocking_count}} blocking, {{suggestion_count}} suggestions\n\n{{findings_block}}\n"
    out = pr.render_comment([_f("style", "suggestion", 1)], tmpl)
    assert "1 suggestion\n" in out.split("\n\n")[0] + "\n" and "1 suggestions" not in out


def test_extra_reasoning_is_plain_markdown_not_small_italic_html():
    from scripts import post_review as pr
    out = pr.render_finding(_f("accuracy", "blocking", 5, reasoning="Wrong default. The code sets `X` to 2 MB."))
    assert "The code sets `X` to 2 MB." in out
    assert "<sub>" not in out and "<i>" not in out
