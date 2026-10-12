## Docs review: 0 blocking, 4 suggestions

Automated review of this PR against the style guide and, where the PR changes behavior, the code. Nothing here blocks merge. Apply what is relevant, then this PR goes through its normal review.


<details>
<summary><code>docs/content/migrate/v3.md:47</code> [style] (suggestion) Style guide, Voice: do not state how a third-party service behaves unless its documentation or the source says so.</summary>

Style guide, Voice: do not state how a third-party service behaves unless its documentation or the source says so. The Go comment (pkg/provider/acme/provider.go:1063) states it, but the migration text gives the reader no link; acme.md already links Let's Encrypt for the related wildcard limit.

> As ACME only issues single-level wildcard certificates, the ACME certificate resolvers refuse a `**.example.com` domain,

**Suggested fix:**
As [ACME only issues single-level wildcard certificates](../reference/install-configuration/tls/certificate-resolvers/acme.md#domain-definition), the ACME certificate resolvers refuse a `**.example.com` domain,

</details>


<details>
<summary><code>docs/content/reference/routing-configuration/http/routing/rules-and-priority.md:57</code> [completeness] (suggestion) pkg/muxer/http/matcher.go:88-90 now makes the Host matcher return an error for any wildcard that is not the catch-all `*` or a `*.`/`**.` p…</summary>

pkg/muxer/http/matcher.go:88-90 now makes the Host matcher return an error for any wildcard that is not the catch-all `*` or a `*.`/`**.` prefix (for example `Host(`foo.*.com`)` or `Host(`*foo.com`)`). That is a user-visible change in what a router rule accepts, and the page does not say where a wildcard may appear. Confirm whether such rules were previously accepted before documenting.

> The `Host` matcher supports a wildcard prefix to match the subdomains of a domain.

**Suggested fix:**
Add after the wildcard description: "A wildcard is valid only as a leading `*.` or `**.` label, or as the catch-all `Host(`*`)`. A rule with a wildcard anywhere else is invalid."

</details>


<details>
<summary><code>docs/content/reference/routing-configuration/http/routing/rules-and-priority.md:241</code> [clarity] (suggestion) Style guide, Clarity Rules: name the concrete noun instead of 'it'.</summary>

Style guide, Clarity Rules: name the concrete noun instead of 'it'. In this sentence 'it' could refer to 'The stars', 'this length', or the host; only the host is meant.

> The stars of a double wildcard host do not count toward this length,
so that it always ranks below the single wildcard and the exact hosts it covers:

**Suggested fix:**
The stars of a double wildcard host do not count toward this length,
so that the double wildcard host always ranks below the single wildcard and the exact hosts it covers:

</details>


<details>
<summary><code>docs/content/reference/routing-configuration/tcp/routing/rules-and-priority.md:219</code> [clarity] (suggestion) Style guide, Clarity Rules: name the concrete noun instead of 'it'.</summary>

Style guide, Clarity Rules: name the concrete noun instead of 'it'. In this sentence 'it' could refer to 'The stars', 'this length', or the host; only the host is meant.

> The stars of a double wildcard host do not count toward this length,
so that it always ranks below the single wildcard and the exact hosts it covers:

**Suggested fix:**
The stars of a double wildcard host do not count toward this length,
so that the double wildcard host always ranks below the single wildcard and the exact hosts it covers:

</details>


<!-- review-doc-pr:v1 -->

<sub>Suggestions are drafts. Verify each against the code before applying. Style findings come from an AI reading the style guide; no linter ran. This check is advisory and never edits the PR. To read a finding in a separate session, fetch this comment's raw body with `gh api repos/<owner>/<repo>/issues/comments/<id>`.</sub>

