# Automated Doc Review for Traefik Proxy Pull Requests: Design

## Goal

When someone opens a pull request on traefik/traefik, an automated check should do two things:

1. If the pull request changes documentation, review that documentation for accuracy against the code, style, links, clarity, and completeness.
2. If the pull request changes user-facing code but no documentation, check whether documentation is needed, and if so, suggest where and what to write.

The check posts one comment. It never edits the pull request and never blocks a merge. A person decides what to do with it.

Today, Proxy CI checks Markdown structure, the docs build, links, spelling, and that generated files are in sync. Nothing checks whether a doc claim matches the code, whether a feature pull request forgot its docs, or whether the writing follows a style guide. Reviewers do that by hand.

## Scope

In scope: a public Proxy style guide, a PR-time review for Proxy docs, the check for missing docs, and suggested doc text.

Out of scope, on purpose:

- Changing existing documentation rules. The style guide documents current practice, including Title Case headings, even though sentence case would be better overall.
- Adding new lint tools such as Vale. Proxy has none, and adding one would change established rules.
- Rewriting existing pages to match the guide.
- Pushing changes to a pull request automatically.
- The planned move from MkDocs to Docusaurus. The design keeps MkDocs-specific rules in one place so they can be swapped later.

## How it works

The diagram is in `2026-10-08-proxy-doc-review-workflow.png`.

| The pull request contains | What runs | What is posted |
|---|---|---|
| Doc changes | Full review of the changed docs. If user-facing code also changed, the missing-docs check runs as well. | One comment with findings, and suggestions for any gaps |
| User-facing code, no doc changes | The missing-docs check only | A comment only if docs are needed, with suggestions |
| Neither (tests, refactors, internal code) | Nothing | Nothing |

Dependency-update pull requests are skipped.

## Components

### One shared engine with a profile for each product

The existing review plugin has five review layers (accuracy, style, reference, clarity, completeness). None of them is specific to Hub. What is specific is a handful of settings and some code that checks the repository name. Those become a small profile file per product: where the docs are, where the source code is, which style guide to read, which doc engine is used, the map from code areas to doc areas, and how the check is run. Hub gets one profile and Proxy gets one. A third product, or the later Docusaurus move, means a new or changed profile, not a new skill.

### Style guide

The guide lives in the Proxy repository, so it is public, and the review reads it from there. The review reads the copy on the pull request's base branch, not on the pull request itself, so a pull request cannot change the rules it is judged by. A bundled copy is used only if the repository copy is missing.

There is no new lint tool. The style layer is judged by the AI against the guide, and it says so in the comment. It only looks at changed lines, so existing pages are not criticized for old habits. For the first release, every style finding is a suggestion, not a blocker, until testing shows how reliable they are.

### Accuracy

In Proxy, the docs and the code are in the same repository. For a pull request, the code in the diff is the main evidence. The review then reads the surrounding code (the option's struct, its defaults, related tests) to check each claim in the changed docs.

### Missing-docs check

For each user-facing code change, the check asks whether documentation is needed and whether the pull request already provides it. User-facing means a new or changed configuration option, command-line flag, default value, or middleware behavior. It reuses the document-type and file-location logic the doc generator already uses, and a shared map from code areas to doc areas (for example, `pkg/config/static` maps to the install configuration reference).

### Suggestions

When docs are needed or incomplete, the comment includes suggestions: the file to change, where in the file, and the suggested text, written to the style guide and based on the code.

- Suggestions are plain text inside the comment. They do not use GitHub's suggested-changes feature, which only works on lines already in the pull request.
- Each suggestion is in a collapsible section so the comment stays short.
- Suggestions are drafts. The comment says so, and a person verifies them.
- The comment has a size cap. If suggestions would exceed it, the comment says what was shortened.
- An external contributor reads the suggestions and applies what they agree with. For an internal pull request, the docs owner applies them with the doc generator, which commits docs to the pull request branch.

### The comment

One comment per pull request, marked so a retry does not post a duplicate. Advisory only.

### Contributor guidelines

The contributing documentation will describe: the style guide, when the review runs and when it stays silent, that suggestions are drafts to verify, and how to ask for a re-run. AGENTS.md gets a one-line pointer to the style guide, because AI assistants read that file automatically.

## Testing before anything is public

1. **Replay on real merged pull requests.** Run the review on 5 to 10 recent merged Proxy pull requests. For ones that included docs, remove the docs from the copy and check that the missing-docs check asks for them. This gives a measured answer, not an impression.
2. **Seeded mistakes.** Create test pull requests with known problems (a wrong default, a missing doc, a style violation, a broken link) and check that each is caught.
3. **Fork stage.** Run the full workflow in a personal fork, posting real comments there.
4. **Dry run upstream.** Run on live upstream pull requests in dry-run mode, which prints the comment without posting.
5. **Go-live bar.** Agree before testing what counts as acceptable, for example how many findings may be wrong or noisy. See open item 6.

## Maintenance

- Shared checklists, the profile format, and the code-to-doc map exist once.
- The style guide has one source file in the Proxy repository.
- The existing manual check that the bundled and repository copies match stays manual, not added to CI.
- When the docs move to Docusaurus, the Proxy profile and the engine-specific rules in the guide change. The review layers do not.

## Open items

These need a decision from the team before or during rollout.

1. **Does the Proxy team agree to run this in their CI?** (for the team)
   - The issue: the check would run as a new workflow in traefik/traefik. The Proxy maintainers own that repository's automation.
   - Why it matters: without their agreement the design cannot go live, however well it tests.
   - Decision needed: whether the maintainers will accept an advisory docs review workflow, and who approves changes to it.
   - Recommendation: build and prove it in a personal fork first, then bring the maintainers a working demo with measured results.
2. **Pull requests from forks and security** (for the team)
   - The issue: most outside contributors open pull requests from their own fork. GitHub does not give forks access to the repository's secrets, so the check cannot call an AI service the normal way. The workaround runs the check with secrets, which means an AI reads text and code written by a stranger. A malicious pull request could hide instructions in its text, trying to make the AI leak secrets or post misleading content.
   - Why it matters: Hub's docs repository only gets internal pull requests, so this problem is new for Proxy.
   - Decision needed: how to run on external pull requests safely.
   - Recommendation: run external pull requests only after a maintainer applies a label, give the AI read-only access, keep secrets out of reach of the part that reads pull request content, and post only through a fixed, limited step.
3. **Which code counts as user-facing?** (clarification)
   - The issue: the missing-docs check should fire for a new option or a changed default, and stay quiet for a refactor or a test. The line between them has to be written down as a list of code areas and change types.
   - Why it matters: too broad and the check spams unrelated pull requests. Too narrow and it misses real gaps.
   - Decision needed: review and approve the initial list of code areas, starting from the map of Proxy code to doc areas.
   - Recommendation: start narrow (configuration structs, flags, and middleware behavior), and widen it after the replay tests.
4. **Who provides the credentials and pays for the runs?** (for the team)
   - The issue: the check calls an AI service and posts comments, which needs an API key and a bot account with permission to comment.
   - Why it matters: it has a running cost, and the key must be stored safely.
   - Decision needed: who owns the account and key, who pays, and whether to cap the cost per pull request.
   - Recommendation: use the same identity approach as the Hub docs check, and set a per-pull-request cost cap from the start.
5. **Where the style guide lives in the repository**
   - The issue: the guide must be in the repo to be public and readable by the review, but the location is not chosen.
   - Why it matters: the location decides the links from the contributing guide, AGENTS.md, and the pull request template.
   - Decision needed: the file path, and whether it is published on the docs site.
   - Recommendation: a page in the contributing section of the docs, so it is both public and in the build.
6. **How good is good enough?** (writer side)
   - The issue: an automated reviewer will sometimes be wrong or noisy. There is no agreed limit yet.
   - Why it matters: without a bar, "ready to go public" is a feeling, and a noisy bot loses contributors' trust.
   - Decision needed: the acceptable rate of wrong or unhelpful findings, and what happens if the tests miss it.
   - Recommendation: set the bar before testing, and keep style findings as suggestions until they pass it.
7. **Hub depends on part of the Proxy docs**
   - The issue: Hub's cli-ref.md is copied from Proxy's install configuration reference, which is generated from code. The style guide uses MkDocs syntax, and Hub renders in a different system.
   - Why it matters: a format change in Proxy could break Hub's build.
   - Decision needed: confirm how Hub's copy step handles MkDocs-only syntax before the guide or check touches those pages.
   - Recommendation: check the copy step first. This is a small investigation, not a design change.
8. **What does the writer do?** (clarification)
   - The writer will incorporate feedback on the skill and maintain it.
   - At what stage, or in which cases does the writer enter the picture? Do they review the doc PRs (external and internal)? Are the issues added into the backlog?
