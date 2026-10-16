## Docs review: 0 blocking, 5 suggestions

<details>
<summary>🟡 <code>http/routing/rules-and-priority.md:238</code> &nbsp;·&nbsp; Accuracy: default priority</summary>

**What's wrong:** This is no longer true for a rule with a `**.` host: the two stars are not counted (pkg/muxer/http/mux.go:85, pkg/muxer/muxer.go:23), so `Host(`**.example.com`)` ranks below the equally long single-label and exact hosts it covers. This page is not part of the PR.

**Suggested fix:**

```diff
- The priority is directly equal to the length of the rule, and so the longest length has the highest priority.
+ The priority is directly equal to the length of the rule, and so the longest length has the highest priority. The two stars of a `**.` double wildcard host do not count, so such a rule ranks below the `*.` wildcard and exact hosts it covers.
```

</details>

<details>
<summary>🟡 <code>tls/certificate-resolvers/acme.md:243</code> &nbsp;·&nbsp; Missing docs: ACME rejects <code>**.</code> domains</summary>

**What's wrong:** A certificate resolver derives its domains from `Host()` and `HostSNI()` matchers. With `**.` now valid in those matchers, a router such as ``Host(`**.example.com`)`` with a `certResolver` is rejected by ACME: the PR adds an explicit error (pkg/provider/acme/provider.go:1062). The page names only the `*.*.` form. This page is not part of the PR.

**Code change:** It is not possible to request a double wildcard certificate for a domain (for example `*.*.local.com`).

**Suggested fix:**

It is not possible to request a double wildcard certificate for a domain (for example `*.*.local.com`).
A `**.` prefix, which the `Host()` and `HostSNI()` matchers accept, is rejected for the same reason: ACME only issues single-level wildcard certificates.

</details>

<details>
<summary>🟡 <code>http/routing/rules-and-priority.md:55</code> &nbsp;·&nbsp; Missing docs: <code>**.</code> double wildcard in Host</summary>

**What's wrong:** The PR adds `Host(`**.example.com`)`, which matches every subdomain of `example.com` at any depth but not `example.com` itself (DomainMatchHostExpression, pkg/muxer/muxer.go:36). It also rejects any other `*` placement with a validation error (pkg/muxer/http/matcher.go:88). The page only describes the single-label `*.` prefix, and the matcher table row says the same. This page is not part of the PR.

**Code change:** pkg/muxer/muxer.go:36: new `**.` double wildcard prefix in Host (matches one or more labels)

**Suggested fix:**

In the "Wildcard subdomain matching" box, after the sentence ending "or `example.com` itself.", add:

```markdown
The `**.` prefix (`**.example.com`) matches subdomains at any depth: `foo.example.com` and `foo.bar.example.com`, but not `example.com` itself.
A wildcard is either a bare `*`, or a `*.` or `**.` prefix followed by a domain. Any other use of `*` in a `Host` value is rejected.
```

In the matcher table, change the `Host(`domain`)` row to end with: "Supports wildcard subdomain matching (e.g. `*.example.com`, `**.example.com`)."

</details>

<details>
<summary>🟡 <code>tcp/routing/rules-and-priority.md:64</code> &nbsp;·&nbsp; Missing docs: <code>**.</code> double wildcard in HostSNI</summary>

**What's wrong:** `hostOrIP` now accepts `**.` (pkg/muxer/tcp/matcher.go:65) and the matching goes through the same `DomainMatchHostExpression`, so `HostSNI(`**.example.com`)` matches subdomains at any depth. The TCP page documents only the single-level `*.` prefix, in the matcher table (line 21) and in the "Wildcard subdomain matching" box. The TCP default priority also loses the two stars (pkg/muxer/tcp/mux.go:114). This page is not part of the PR.

**Code change:** pkg/muxer/tcp/matcher.go:65: HostSNI now accepts the `**.` double wildcard prefix

**Suggested fix:**

In the "Wildcard subdomain matching" box, after the sentence ending "or `example.com` itself.", add:

```markdown
The `**.` prefix (`**.example.com`) matches subdomains at any depth: `foo.example.com` and `foo.bar.example.com`, but not `example.com` itself.
The two stars of a `**.` prefix do not count in the default priority of the rule.
```

In the matcher table, change the `HostSNI(`domain`)` row to end with: "Supports wildcard subdomain matching (e.g. `*.example.com`, `**.example.com`)."

</details>

<details>
<summary>🟡 <code>content/migrate/v3.md:416</code> &nbsp;·&nbsp; Missing docs: stricter Host wildcard validation</summary>

**What's wrong:** The `Host` matcher now rejects wildcards that are not a bare `*` or a `*.`/`**.` prefix (pkg/muxer/http/matcher.go:88). A rule such as ``Host(`*.*.example.com`)`` or ``Host(`foo*.example.com`)`` that was accepted before now fails. Earlier behavior changes of this kind got a note in this file (the section above, for the bare `*`). This page is not part of the PR.

**Code change:** ### Wildcard Host matcher

**Suggested fix:**

Add a section for the release this ships in, above `## v3.7.7`:

```markdown
### Host matcher wildcard validation

From version `<version>` onwards, a `*` in a `Host` value must be either the bare catch-all `*`, or a `*.` or `**.` prefix followed by a domain.
Any other use of `*`, for example ``Host(`foo*.example.com`)`` or ``Host(`*.*.example.com`)``, is rejected with a validation error.
Use `HostRegexp` for other patterns.
```

</details>

<!-- review-doc-pr:v1 -->

<sub>Suggestions are drafts: verify each against the code before applying. Advisory only; this never edits the PR or blocks merge. Style findings are AI-judged against the style guide (no linter ran).</sub>

