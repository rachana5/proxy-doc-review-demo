## Docs review: 0 blocking, 2 suggestions

Automated review of this PR against the style guide and, where the PR changes behavior, the code. Nothing here blocks merge. Apply what is relevant, then this PR goes through its normal review.


<details>
<summary><code>docs/content/migrate/v3.md:48</code> [style] (suggestion) Style guide, Titles and Headings: every heading you add uses Title Case, even on a page whose other headings use another case.</summary>

Style guide, Titles and Headings: every heading you add uses Title Case, even on a page whose other headings use another case. The text after the colon is lowercase.

> ### OpenTelemetry Metrics: exponential histograms

**Suggested fix:**
### OpenTelemetry Metrics: Exponential Histograms

</details>


<details>
<summary><code>docs/content/reference/install-configuration/observability/metrics.md:71</code> [completeness] (suggestion) The PR makes the standard OpenTelemetry environment variable the way to switch these histograms to exponential buckets (otel.go:245-253, te…</summary>

The PR makes the standard OpenTelemetry environment variable the way to switch these histograms to exponential buckets (otel.go:245-253, test otel_test.go:455-523, accepts explicit_bucket_histogram and base2_exponential_bucket_histogram). The migrate page and the explicitBoundaries row mention it, but no reference or observe page says how to enable exponential histograms.

> pkg/observability/metrics/otel.go: traefik_*_request_duration_seconds histograms now follow OTEL_EXPORTER_OTLP_METRICS_DEFAULT_HISTOGRAM_AGGREGATION

**Suggested fix:**
Add after the OpenTelemetry options table: "To export the request duration histograms as exponential histograms, set the OTEL_EXPORTER_OTLP_METRICS_DEFAULT_HISTOGRAM_AGGREGATION environment variable to base2_exponential_bucket_histogram. The default is explicit_bucket_histogram." Confirm the default and value names against the OpenTelemetry specification before publishing.

</details>


<!-- review-doc-pr:v1 -->

<sub>Suggestions are drafts. Verify each against the code before applying. Style findings come from an AI reading the style guide; no linter ran. This check is advisory and never edits the PR. To read a finding in a separate session, fetch this comment's raw body with `gh api repos/<owner>/<repo>/issues/comments/<id>`.</sub>

