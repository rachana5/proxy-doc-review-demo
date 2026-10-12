## Docs review: 2 blocking, 4 suggestions

<details>
<summary>🔴 <code>middlewares/retry.md:7</code> &nbsp;·&nbsp; Broken link</summary>

**What's wrong:** Link does not resolve to a page in the built site: ../../../routing/not-a-real-page.md

> ../../../routing/not-a-real-page.md

**Suggested fix:**

(needs a human to identify the correct target)

</details>

<details>
<summary>🔴 <code>middlewares/retry.md:101</code> &nbsp;·&nbsp; Accuracy: default value</summary>

**What's wrong:** The default is 2 MB, not 1 MB. `RetryDefaultMaxRequestBodyBytes` is `2 * 1024 * 1024` (pkg/config/dynamic/middlewares.go:17) and pkg/middlewares/retry/retry.go:109 uses it when the option is unset.

**Suggested fix:**

```diff
- | 1MB | No |
+ | 2MB | No |
```

</details>

<details>
<summary>🟡 <code>middlewares/retry.md:7</code> &nbsp;·&nbsp; Style guide: Words and Phrases to Avoid</summary>

**What's wrong:** "leverages" is a word the guide replaces with "uses", and "robust, seamless" describes nothing specific.

**Suggested fix:**

```diff
- It leverages exponential backoff to provide a robust, seamless retry experience.
+ The middleware waits longer between each retry when you set `initialInterval`, so a failing backend gets time to recover.
```

</details>

<details>
<summary>🟡 <code>middlewares/retry.md:7</code> &nbsp;·&nbsp; Style guide: Words and Phrases to Avoid</summary>

**What's wrong:** A rhetorical question. The guide asks for a statement of the fact instead.

**Suggested fix:**

```diff
- But what if you need more control?
+ To control how long retries continue, set `timeout`.
```

</details>

<details>
<summary>🟡 <code>middlewares/retry.md:7</code> &nbsp;·&nbsp; Style guide: Voice</summary>

**What's wrong:** The sentence starts with "Please" and joins two clauses with an em dash.

**Suggested fix:**

```diff
- Please see the [timeouts guide](../../../routing/not-a-real-page.md) — it covers this.
+ See the [timeouts guide](../../../routing/not-a-real-page.md). It covers the retry `timeout` option.
```

</details>

<details>
<summary>🟡 <code>middlewares/retry.md:7</code> &nbsp;·&nbsp; Style guide: Clarity Rules</summary>

**What's wrong:** "it" and "this" have no noun in the same sentence. A reader scanning the page cannot tell what the guide covers.

**Suggested fix:**

```diff
- it covers this
+ The timeouts guide explains how `timeout` limits total retry time.
```

</details>

<!-- review-doc-pr:v1 -->

<sub>Suggestions are drafts: verify each against the code before applying. Advisory only; this never edits the PR or blocks merge. Style findings are AI-judged against the style guide (no linter ran).</sub>

