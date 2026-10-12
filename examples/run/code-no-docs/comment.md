## Docs review: 0 blocking, 1 suggestion

<details>
<summary>🟡 <code>http/middlewares/retry.md:95</code> &nbsp;·&nbsp; Missing docs: new <code>maxBackoff</code> option</summary>

**What's wrong:** This PR adds a user-configurable `maxBackoff` option to the Retry middleware but changes no documentation. The Retry options table (Configuration Options) and the examples in all five formats do not mention it.

**Code change:** pkg/config/dynamic/middlewares.go: new Retry option "maxBackoff" (ptypes.Duration)

**Suggested fix:**

Add a row to the Configuration Options table, after `initialInterval`:

```markdown
| <a id="opt-maxBackoff" href="#opt-maxBackoff" title="#opt-maxBackoff">`maxBackoff`</a> | Upper bound on the wait time between two retries. <br /> If unspecified, the wait time is capped at twice the `initialInterval`. <br /> Defined in seconds or as a valid duration format, see [time.ParseDuration](https://golang.org/pkg/time/#ParseDuration). | 0 | No |
```

Add `maxBackoff: 1s` to the Structured (YAML), Structured (TOML), Labels, Tags, and Kubernetes examples, next to `initialInterval`, so each format produces the same configuration.

Before applying: this diff only adds the struct field. `pkg/middlewares/retry/retry.go` does not read `MaxBackoff`, so confirm the behavior and the default before publishing. Also run `make generate` so the generated CRD files pick up the new field; do not edit them by hand.

</details>

<!-- review-doc-pr:v1 -->

<sub>Suggestions are drafts: verify each against the code before applying. Advisory only; this never edits the PR or blocks merge. Style findings are AI-judged against the style guide (no linter ran).</sub>

