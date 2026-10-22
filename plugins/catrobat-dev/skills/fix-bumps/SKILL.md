---
name: fix-bumps
description: >-
  Diagnose and fix dependency-bump PRs (Dependabot/Renovate) whose CI is red: read the failing
  job, classify the failure (upstream regression, new lint rule, real breaking change, flake),
  fix it properly, and open a PR that supersedes the bot's. Use for "/fix-bumps", "fix the red
  bumps", "why is this dependabot PR failing".
---

# fix-bumps — a red bump is a diagnosis nobody has done yet

Never just skip a red bump: that is how one stays red for months while every other bump lands.

## 1. Find them

```bash
gh pr list --repo <org/repo> --state open \
  --json number,title,author,mergeable,statusCheckRollup
```

Bot-authored with any failing check. **Check the default branch first** — if it is red too, the
bump is innocent; fix the real problem instead and say so:

```bash
gh run list --repo <org/repo> --branch <default> --limit 5 --json conclusion,workflowName
```

## 2. Read the actual error

`gh pr checks <n> --repo <org/repo>` names the failing jobs, then
`gh run view --repo <org/repo> --job <id> --log-failed`.

- Progress bars drown the log: `| grep -vE '[▓░]'`.
- The tail is post-job cleanup. The real message sits mid-log, after the test summary — grep
  for `error|exception|failed|not found`.
- **When many jobs fail, read the cheapest one.** Twenty red UI jobs and one red unit-test job
  usually share a root cause; the short log answers it.

## 3. Classify before touching code

| shape | tell | fix |
|---|---|---|
| upstream regression | the bump's changelog or issues describe it; the failure is in vendor code | bump or pin the *other* dependency that carries the fix — don't skip the bump |
| new lint/analysis rule | the tool version added a rule about code you already had | fix the code; the rule is usually right |
| real breaking change | your code calls a changed API | migrate the calls; if that is a project, say so and stop |
| flake / infra | passes on re-run, or fails in setup with no code signal | re-run once; if it recurs it is not a flake |

**Search upstream before theorising** — the highest-value minute of this skill:

```bash
gh api repos/<vendor>/<pkg>/releases/tags/<version> --jq .body
gh search issues --repo <vendor>/<pkg> --limit 15 "<version>"
```

Worked example (Catroweb #7099): a doctrine/orm patch release called an API that only existed in
an unreleased DBAL version; the test schema was never created and every test failed with
"table doesn't exist". The error message pointed at a missing table; two upstream issues named
the real cause. The fix was one line in `composer.json`.

## 4. Fix and verify locally

Work in a worktree off the default branch — never move someone's checkout off their branch:

```bash
git worktree add ../fix-bump origin/<default>
```

Run the **specific** check that failed, not the whole suite (one Gradle task, one phpstan file,
the affected tests). Show the error before the fix and its absence after.

Package-manager resolvers drift on transitive dependencies (Composer, Gradle). Name the versions
you mean explicitly, then confirm the lockfile diff contains only what you intended. Revert
files the tooling touched incidentally.

## 5. Open a superseding PR

One concern per PR — a bump and an unrelated lint fix are two PRs. The body says what broke,
links upstream, explains why this fix and not a skip, and what you verified. Write
`Supersedes #<n>`; Dependabot closes its own PR on its next run after the bump lands. Then hand
it to `/pr-quality`.

## Do not

- Pin or `ignore` a dependency without an identified reason — both mean "we understand this and
  choose to wait", never "it was red".
- Force-push to a shared branch, or merge your own fix without a maintainer.
