## Docs review: 2 blocking, 4 suggestions

Automated review of this PR against the code and the style guide. Nothing here blocks merge. Apply what is relevant, then this PR goes through its normal review.


<details>
<summary><code>docs/content/reference/routing-configuration/http/middlewares/retry.md:7</code> [style] (suggestion) Style guide, Words and Phrases to Avoid: replace "leverages" with "uses", and replace "robust, seamless" with the specific fact.</summary>

> It leverages exponential backoff to provide a robust, seamless retry experience.

**Suggested fix:**
The middleware waits longer between each retry when you set `initialInterval`, so a failing backend gets time to recover.

</details>


<details>
<summary><code>docs/content/reference/routing-configuration/http/middlewares/retry.md:7</code> [style] (suggestion) Style guide, Words and Phrases to Avoid: rhetorical questions. Write a statement.</summary>

> But what if you need more control?

**Suggested fix:**
To control how long retries continue, set `timeout`.

</details>


<details>
<summary><code>docs/content/reference/routing-configuration/http/middlewares/retry.md:7</code> [style] (suggestion) Style guide, Voice: omit "please". Style guide, Words and Phrases to Avoid: em dash used as a connector.</summary>

> Please see the [timeouts guide](../../../routing/not-a-real-page.md) — it covers this.

**Suggested fix:**
See the [timeouts guide](../../../routing/not-a-real-page.md). It covers the retry `timeout` option.

</details>


<details>
<summary><code>docs/content/reference/routing-configuration/http/middlewares/retry.md:7</code> [reference] (blocking) Relative link target does not exist on disk: docs/content/reference/routing/not-a-real-page.md</summary>

> ../../../routing/not-a-real-page.md

**Suggested fix:**
(needs a human to identify the correct target)

</details>


<details>
<summary><code>docs/content/reference/routing-configuration/http/middlewares/retry.md:7</code> [clarity] (suggestion) "it" and "this" have no noun in the same sentence. A reader scanning the page cannot tell what the guide covers.</summary>

> it covers this

**Suggested fix:**
Name the topic, for example: "The timeouts guide explains how `timeout` limits total retry time."

</details>


<details>
<summary><code>docs/content/reference/routing-configuration/http/middlewares/retry.md:101</code> [accuracy] (blocking) The default is 2 MB, not 1 MB. `RetryDefaultMaxRequestBodyBytes` is `2 * 1024 * 1024` (pkg/config/dynamic/middlewares.go:17) and pkg/middlewares/retry/retry.go:109 uses it when the option is unset.</summary>

> | 1MB | No |

**Suggested fix:**
Change the Default cell to `2MB`.

</details>


<!-- review-doc-pr:v1 -->

<sub>Suggestions are drafts. Verify each against the code before applying. Style findings come from an AI reading the style guide; no linter ran. This check is advisory and never edits the PR. To read a finding in a separate session, fetch this comment's raw body with `gh api repos/<owner>/<repo>/issues/comments/<id>`.</sub>

