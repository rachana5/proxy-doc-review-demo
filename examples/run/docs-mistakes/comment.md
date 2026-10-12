## Docs review: 2 blocking, 4 suggestions

<details>
<summary>🔴 <code>middlewares/retry.md:7</code> &nbsp;Link does not resolve to a page in the built site: ../../../routing/not-a-real-page.md</summary>

> ../../../routing/not-a-real-page.md

(needs a human to identify the correct target)

</details>

<details>
<summary>🔴 <code>middlewares/retry.md:101</code> &nbsp;The default is 2 MB, not 1 MB.</summary>

`RetryDefaultMaxRequestBodyBytes` is `2 * 1024 * 1024` (pkg/config/dynamic/middlewares.go:17) and pkg/middlewares/retry/retry.go:109 uses it when the option is unset.

```diff
- | 1MB | No |
+ | 2MB | No |
```

</details>

<details>
<summary>🟡 <code>middlewares/retry.md:7</code> &nbsp;Style guide, Words and Phrases to Avoid: replace "leverages" with "uses", and replace "robust, seamless" with the specific fact.</summary>

```diff
- It leverages exponential backoff to provide a robust, seamless retry experience.
+ The middleware waits longer between each retry when you set `initialInterval`, so a failing backend gets time to recover.
```

</details>

<details>
<summary>🟡 <code>middlewares/retry.md:7</code> &nbsp;Style guide, Words and Phrases to Avoid: rhetorical questions.</summary>

Write a statement.

```diff
- But what if you need more control?
+ To control how long retries continue, set `timeout`.
```

</details>

<details>
<summary>🟡 <code>middlewares/retry.md:7</code> &nbsp;Style guide, Voice: omit "please".</summary>

Style guide, Words and Phrases to Avoid: em dash used as a connector.

```diff
- Please see the [timeouts guide](../../../routing/not-a-real-page.md) — it covers this.
+ See the [timeouts guide](../../../routing/not-a-real-page.md). It covers the retry `timeout` option.
```

</details>

<details>
<summary>🟡 <code>middlewares/retry.md:7</code> &nbsp;"it" and "this" have no noun in the same sentence.</summary>

A reader scanning the page cannot tell what the guide covers.

```diff
- it covers this
+ The timeouts guide explains how `timeout` limits total retry time.
```

</details>

<!-- review-doc-pr:v1 -->

<sub>Suggestions are drafts: verify each against the code before applying. Advisory only; this never edits the PR or blocks merge. Style findings are AI-judged against the style guide (no linter ran).</sub>

