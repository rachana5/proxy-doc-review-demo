## Docs review: 0 blocking, 4 suggestions

<details>
<summary>🟡 <code>certificate-resolvers/acme.md:243</code> &nbsp;Domains starting with <code>**.</code> are now rejected by the ACME provider with an error (sanitizeDomains, provider.go:1062-1065; test provider_test…</summary>

<sub><i>Line 243 only mentions the <code>*.*.local.com</code> double wildcard; a user who adds <code>**.example.com</code> to a route and a certificate domain would hit the new error. Same PR also skips default-cert generation when no valid domain remains (provider.go:621-624), which needs no doc.</i></sub>

> pkg/provider/acme/provider.go:1062-1065: **. domain rejected, "ACME does not allow '**.' wildcard domain"

Extend line 243:

It is not possible to request a double wildcard certificate for a domain (for example `*.*.local.com` or `**.local.com`). The `**.` prefix is supported by the `Host` and `HostSNI` router matchers only; request a `*.example.com` certificate to cover single-level subdomains.

</details>

<details>
<summary>🟡 <code>routing/rules-and-priority.md:55</code> &nbsp;Host now accepts a double wildcard prefix (<code>**.example.com</code>) matching one or more labels (DomainMatchHostExpression, pkg/muxer/muxer.go:34-…</summary>

<sub><i>The page only documents the single-level <code>*.</code> wildcard. The same PR also makes Host return an error for any other wildcard placement (matcher.go:88-91; tests 'bare double wildcard' <code>Host(</code>**<code>)</code> and 'wildcard not as a prefix' <code>Host(</code>*.*.example.com<code>)</code>, matcher_test.go:271-280), which is user-visible for rules that previously loaded.</i></sub>

> pkg/muxer/http/matcher.go:71,88-91 and pkg/muxer/muxer.go:30-37: Host matcher accepts a "**." prefix; other wildcard shapes now rejected

Extend the 'Wildcard subdomain matching' admonition (line 55) with:

The `Host` matcher also supports a double wildcard prefix (`**.example.com`) to match all subdomains of `example.com`, at any depth: `**.example.com` matches `foo.example.com` and `foo.bar.example.com`, but not `example.com` itself.

A wildcard is valid only as the whole host (`*`, see the exception below), or as a `*.` or `**.` prefix followed by a host without further wildcards. Any other use, such as ``Host(`*.*.example.com`)``, is rejected with an error.

Also add a row to the examples table: ``Match all subdomains of `example.com`, at any depth.`` | ```Host(`**.example.com`)```.

Note: the TLS-option and v2-syntax statements need checking for `**.` before being added.

</details>

<details>
<summary>🟡 <code>routing/rules-and-priority.md:238</code> &nbsp;The default priority is no longer exactly the rule length: for each <code>**.</code> host in the rule the two stars are not counted (DoubleWildcardPen…</summary>

<sub><i>The page states 'The priority is directly equal to the length of the rule', which is now incomplete. The same sentence appears on the TCP page (line 210, HostSNI only).</i></sub>

> pkg/muxer/http/mux.go:75-89 and pkg/muxer/tcp/mux.go:96-117: GetRulePriority subtracts muxer.DoubleWildcardPenalty

Replace the sentence at line 238 (and the equivalent at tcp/routing/rules-and-priority.md line 210) with:

The priority is equal to the length of the rule, and so the longest length has the highest priority. The two stars of a double wildcard host (`**.example.com`) do not count, so a router using one has a lower priority than a router using `*.example.com` or an exact host for the same domain.

</details>

<details>
<summary>🟡 <code>routing/rules-and-priority.md:62</code> &nbsp;HostSNI now accepts a <code>**.</code> prefix (regexp at pkg/muxer/tcp/matcher.go:65, tests matcher_test.go:143-172), but the TCP page documents only…</summary>

<sub><i>Whether the double wildcard matches one-or-more labels for SNI goes through the shared muxer.DomainMatchHostExpression, so it follows the same semantics as HTTP.</i></sub>

> pkg/muxer/tcp/matcher.go:65: hostOrIP = `^(\*\*?\.)?[[:word:]\.\-\:]+$`

Extend the 'Wildcard subdomain matching' admonition (line 62) with:

The `HostSNI` matcher also supports a double wildcard prefix (`**.example.com`) to match all subdomains of `example.com`, at any depth: `**.example.com` matches `foo.example.com` and `foo.bar.example.com`, but not `example.com` itself.

And add a tab to the examples (near line 92): ```HostSNI(`**.example.com`)```.

</details>

<!-- review-doc-pr:v1 -->

<sub>Suggestions are drafts: verify each against the code before applying. Advisory only; this never edits the PR or blocks merge. Style findings are AI-judged against the style guide (no linter ran).</sub>

