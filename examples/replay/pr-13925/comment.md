## Docs review: 0 blocking, 1 suggestions

Automated review of this PR against the style guide and, where the PR changes behavior, the code. Nothing here blocks merge. Apply what is relevant, then this PR goes through its normal review.


<details>
<summary><code>docs/content/reference/routing-configuration/kubernetes/ingress-nginx.md:404</code> [reference] (suggestion) The anchor fix is correct (the target heading is `## AccessLogs`, so `#accesslogs` resolves; the old `#access-logs` did not).</summary>

The anchor fix is correct (the target heading is `## AccessLogs`, so `#accesslogs` resolves; the old `#access-logs` did not). The link still uses the rendered-URL form while the other links this PR touches were converted to source `.md` paths. Both resolve in the built site; the .md form also lets the MkDocs link validation catch breakage. Low-value consistency note. (scripts.check_links reported this link as broken because it resolves directory-style URLs on disk; that is a checker false positive, as are its 4 other findings on unchanged lines 372, 410-412.)

> [install configuration](../../../install-configuration/observability/logs-and-accesslogs/#accesslogs)

**Suggested fix:**
[install configuration](../../install-configuration/observability/logs-and-accesslogs.md#accesslogs)

</details>


<!-- review-doc-pr:v1 -->

<sub>Suggestions are drafts. Verify each against the code before applying. Style findings come from an AI reading the style guide; no linter ran. This check is advisory and never edits the PR. To read a finding in a separate session, fetch this comment's raw body with `gh api repos/<owner>/<repo>/issues/comments/<id>`.</sub>

