## Docs review: 0 blocking, 2 suggestions

<details>
<summary>🟡 <code>content/migrate/v3.md:48</code> &nbsp;·&nbsp; Style guide: Titles and Headings</summary>

**What's wrong:** Every heading you add uses Title Case, even on a page whose other headings use another case. The text after the colon is lowercase.

**Suggested fix:**

```diff
- ### OpenTelemetry Metrics: exponential histograms
+ ### OpenTelemetry Metrics: Exponential Histograms
```

</details>

<details>
<summary>🟡 <code>install-configuration/observability/metrics.md:71</code> &nbsp;·&nbsp; Missing docs: how to enable exponential histograms</summary>

**What's wrong:** The PR makes the standard OpenTelemetry environment variable the way to switch these histograms to exponential buckets (otel.go:245-253, test otel_test.go:455-523, accepts explicit_bucket_histogram and base2_exponential_bucket_histogram). The migrate page and the explicitBoundaries row mention it, but no reference or observe page says how to enable exponential histograms.

**Code change:** pkg/observability/metrics/otel.go: traefik_*_request_duration_seconds histograms now follow OTEL_EXPORTER_OTLP_METRICS_DEFAULT_HISTOGRAM_AGGREGATION

**Suggested fix:**

Add after the OpenTelemetry options table: "To export the request duration histograms as exponential histograms, set the OTEL_EXPORTER_OTLP_METRICS_DEFAULT_HISTOGRAM_AGGREGATION environment variable to base2_exponential_bucket_histogram. The default is explicit_bucket_histogram." Confirm the default and value names against the OpenTelemetry specification before publishing.

</details>

<!-- review-doc-pr:v1 -->

<sub>Suggestions are drafts: verify each against the code before applying. Advisory only; this never edits the PR or blocks merge. Style findings are AI-judged against the style guide (no linter ran).</sub>

