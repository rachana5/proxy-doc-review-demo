## Docs review: 0 blocking, 1 suggestions

Automated review of this PR against the code and the style guide. Nothing here blocks merge. Apply what is relevant, then this PR goes through its normal review.


<details>
<summary><code>docs/content/reference/routing-configuration/http/middlewares/retry.md:95</code> [completeness] (suggestion) This PR adds a user-configurable `maxBackoff` option to the Retry middleware but changes no documentation. The Retry options table (Configuration Options) and the examples in all five formats do not mention it.</summary>

> pkg/config/dynamic/middlewares.go: new Retry option "maxBackoff" (ptypes.Duration)

**Suggested fix:**
Add a row to the Configuration Options table, after `initialInterval`:

```markdown
| <a id="opt-maxBackoff" href="#opt-maxBackoff" title="#opt-maxBackoff">`maxBackoff`</a> | Upper bound on the wait time between two retries. <br /> If unspecified, the wait time is capped at twice the `initialInterval`. <br /> Defined in seconds or as a valid duration format, see [time.ParseDuration](https://golang.org/pkg/time/#ParseDuration). | 0 | No |
```

Add `maxBackoff: 1s` to the Structured (YAML), Structured (TOML), Labels, Tags, and Kubernetes examples, next to `initialInterval`, so each format produces the same configuration.

Before applying: this diff only adds the struct field. `pkg/middlewares/retry/retry.go` does not read `MaxBackoff`, so confirm the behavior and the default before publishing. Also run `make generate` so the generated CRD files pick up the new field; do not edit them by hand.

</details>


<!-- review-doc-pr:v1 -->

<sub>Suggestions are drafts. Verify each against the code before applying. Style findings come from an AI reading the style guide; no linter ran. This check is advisory and never edits the PR. To read a finding in a separate session, fetch this comment's raw body with `gh api repos/<owner>/<repo>/issues/comments/<id>`.</sub>

