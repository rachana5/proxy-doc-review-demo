import pytest
from scripts import pr_filter, profile


def test_both_shipped_profiles_load():
    assert profile.load("proxy")["engine"] == "mkdocs"
    assert profile.load("hub")["engine"] == "docusaurus"


def test_missing_required_key_fails(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text('{"name": "x"}')
    with pytest.raises(ValueError):
        profile.load(str(bad))


def test_profile_driven_bot_skip():
    p = profile.load("proxy")
    assert pr_filter.is_excluded_pr_for_profile(author_login="app/dependabot", title="x", profile=p)
    assert pr_filter.is_excluded_pr_for_profile(author_login="a", title="chore(deps): bump", profile=p)
    assert not pr_filter.is_excluded_pr_for_profile(author_login="a", title="docs: fix", profile=p)
