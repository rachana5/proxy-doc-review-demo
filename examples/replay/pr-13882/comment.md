## Docs review: 0 blocking, 4 suggestions

<details>
<summary>🟡 <code>migrate/v3.md:47</code> &nbsp;Style guide, Voice: do not state how a third-party service behaves unless its documentation or the source says so.</summary>

<sub><i>The Go comment (pkg/provider/acme/provider.go:1063) states it, but the migration text gives the reader no link; acme.md already links Let's Encrypt for the related wildcard limit.</i></sub>

```diff
- As ACME only issues single-level wildcard certificates, the ACME certificate resolvers refuse a `**.example.com` domain,
+ As [ACME only issues single-level wildcard certificates](../reference/install-configuration/tls/certificate-resolvers/acme.md#domain-definition), the ACME certificate resolvers refuse a `**.example.com` domain,
```

</details>

<details>
<summary>🟡 <code>routing/rules-and-priority.md:57</code> &nbsp;pkg/muxer/http/matcher.go:88-90 now makes the Host matcher return an error for any wildcard that is not the catch-all <code>*</code> or a <code>*.</code>/<code>**.</code> p…</summary>

<sub><i>That is a user-visible change in what a router rule accepts, and the page does not say where a wildcard may appear. Confirm whether such rules were previously accepted before documenting.</i></sub>

> The `Host` matcher supports a wildcard prefix to match the subdomains of a domain.

Add after the wildcard description: "A wildcard is valid only as a leading `*.` or `**.` label, or as the catch-all `Host(`*`)`. A rule with a wildcard anywhere else is invalid."

</details>

<details>
<summary>🟡 <code>routing/rules-and-priority.md:241</code> &nbsp;Style guide, Clarity Rules: name the concrete noun instead of 'it'.</summary>

<sub><i>In this sentence 'it' could refer to 'The stars', 'this length', or the host; only the host is meant.</i></sub>

> The stars of a double wildcard host do not count toward this length,
> so that it always ranks below the single wildcard and the exact hosts it covers:

The stars of a double wildcard host do not count toward this length,
so that the double wildcard host always ranks below the single wildcard and the exact hosts it covers:

</details>

<details>
<summary>🟡 <code>routing/rules-and-priority.md:219</code> &nbsp;Style guide, Clarity Rules: name the concrete noun instead of 'it'.</summary>

<sub><i>In this sentence 'it' could refer to 'The stars', 'this length', or the host; only the host is meant.</i></sub>

> The stars of a double wildcard host do not count toward this length,
> so that it always ranks below the single wildcard and the exact hosts it covers:

The stars of a double wildcard host do not count toward this length,
so that the double wildcard host always ranks below the single wildcard and the exact hosts it covers:

</details>

<!-- review-doc-pr:v1 -->

<sub>Suggestions are drafts: verify each against the code before applying. Advisory only; this never edits the PR or blocks merge. Style findings are AI-judged against the style guide (no linter ran).</sub>

