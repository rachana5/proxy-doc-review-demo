## Docs review: 0 blocking, 4 suggestions

<details>
<summary>🟡 <code>tls/certificate-resolvers/acme.md:243</code> &nbsp;·&nbsp; Missing docs: ACME rejects <code>**.</code> domains</summary>

**What's wrong:** Domains starting with `**.` are now rejected by the ACME provider with an error (sanitizeDomains, provider.go:1062-1065; test provider_test.go:221-235). Line 243 only mentions the `*.*.local.com` double wildcard; a user who adds `**.example.com` to a route and a certificate domain would hit the new error. Same PR also skips default-cert generation when no valid domain remains (provider.go:621-624), which needs no doc.

**Code change:** pkg/provider/acme/provider.go:1062-1065: **. domain rejected, "ACME does not allow '**.' wildcard domain"

**Suggested fix:**

Extend line 243:

It is not possible to request a double wildcard certificate for a domain (for example `*.*.local.com` or `**.local.com`). The `**.` prefix is supported by the `Host` and `HostSNI` router matchers only; request a `*.example.com` certificate to cover single-level subdomains.

</details>

<details>
<summary>🟡 <code>http/routing/rules-and-priority.md:55</code> &nbsp;·&nbsp; Missing docs: <code>**.</code> in Host rules</summary>

**What's wrong:** Host now accepts a double wildcard prefix (`**.example.com`) matching one or more labels (DomainMatchHostExpression, pkg/muxer/muxer.go:34-37; test matcher_test.go:281-290). The page only documents the single-level `*.` wildcard. The same PR also makes Host return an error for any other wildcard placement (matcher.go:88-91; tests 'bare double wildcard' `Host(`**`)` and 'wildcard not as a prefix' `Host(`*.*.example.com`)`, matcher_test.go:271-280), which is user-visible for rules that previously loaded.

**Code change:** pkg/muxer/http/matcher.go:71,88-91 and pkg/muxer/muxer.go:30-37: Host matcher accepts a "**." prefix; other wildcard shapes now rejected

**Suggested fix:**

Extend the 'Wildcard subdomain matching' admonition (line 55) with:

The `Host` matcher also supports a double wildcard prefix (`**.example.com`) to match all subdomains of `example.com`, at any depth: `**.example.com` matches `foo.example.com` and `foo.bar.example.com`, but not `example.com` itself.

A wildcard is valid only as the whole host (`*`, see the exception below), or as a `*.` or `**.` prefix followed by a host without further wildcards. Any other use, such as ``Host(`*.*.example.com`)``, is rejected with an error.

Also add a row to the examples table: ``Match all subdomains of `example.com`, at any depth.`` | ```Host(`**.example.com`)```.

Note: the TLS-option and v2-syntax statements need checking for `**.` before being added.

</details>

<details>
<summary>🟡 <code>http/routing/rules-and-priority.md:238</code> &nbsp;·&nbsp; Missing docs: default priority with <code>**.</code></summary>

**What's wrong:** The default priority is no longer exactly the rule length: for each `**.` host in the rule the two stars are not counted (DoubleWildcardPenalty, pkg/muxer/muxer.go:19-25 returns len("**")), so a double wildcard ranks below the single wildcard and exact hosts it covers whatever their lengths. The page states 'The priority is directly equal to the length of the rule', which is now incomplete. The same sentence appears on the TCP page (line 210, HostSNI only).

**Code change:** pkg/muxer/http/mux.go:75-89 and pkg/muxer/tcp/mux.go:96-117: GetRulePriority subtracts muxer.DoubleWildcardPenalty

**Suggested fix:**

Replace the sentence at line 238 (and the equivalent at tcp/routing/rules-and-priority.md line 210) with:

The priority is equal to the length of the rule, and so the longest length has the highest priority. The two stars of a double wildcard host (`**.example.com`) do not count, so a router using one has a lower priority than a router using `*.example.com` or an exact host for the same domain.

</details>

<details>
<summary>🟡 <code>tcp/routing/rules-and-priority.md:62</code> &nbsp;·&nbsp; Missing docs: <code>**.</code> in HostSNI rules</summary>

**What's wrong:** HostSNI now accepts a `**.` prefix (regexp at pkg/muxer/tcp/matcher.go:65, tests matcher_test.go:143-172), but the TCP page documents only the single-level `*.` wildcard. Whether the double wildcard matches one-or-more labels for SNI goes through the shared muxer.DomainMatchHostExpression, so it follows the same semantics as HTTP.

**Code change:** pkg/muxer/tcp/matcher.go:65: hostOrIP = `^(\*\*?\.)?[[:word:]\.\-\:]+$`

**Suggested fix:**

Extend the 'Wildcard subdomain matching' admonition (line 62) with:

The `HostSNI` matcher also supports a double wildcard prefix (`**.example.com`) to match all subdomains of `example.com`, at any depth: `**.example.com` matches `foo.example.com` and `foo.bar.example.com`, but not `example.com` itself.

And add a tab to the examples (near line 92): ```HostSNI(`**.example.com`)```.

</details>

<!-- review-doc-pr:v1 -->

<sub>Suggestions are drafts: verify each against the code before applying. Advisory only; this never edits the PR or blocks merge. Style findings are AI-judged against the style guide (no linter ran).</sub>

