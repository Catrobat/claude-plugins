---
name: public-fit
description: >-
  Check that a diff, commit, PR body, or comment is safe to publish in a public Catrobat
  repository: no secrets, no personal data (the users are children), no private details about the
  contributor (local paths, machine, employer, private email), and good enough to sign. Use for
  "public-fit", "is this safe to push", "check before PR", or before anything leaves the machine.
---

# public-fit — safe to publish?

Catrobat repositories are public. A push is irreversible in practice: forks, `refs/pull/*`, and
code-search indexes keep a blob after you delete it. There is no undo, only rotation.

## Scope

Default: the working-tree diff plus commits not on the base branch, **and** any text you are
about to post (commit message, PR body, comment). Say what you read.

## Pass 1 — leaks (blocking)

Check every hit by hand; a grep hit is a candidate, not a verdict.

- **Credentials.** API keys, tokens, `Bearer `, private keys, keystore passwords, `.env` files
  with real values, `local.properties`, signing configs, basic-auth URLs. A rotated key is still
  a finding — it names the service.
- **User data.** Real usernames, emails, project files, screenshots or recorded HTTP fixtures
  from production. Catrobat's users are largely children: real user data never goes in a
  fixture, test, screenshot, log, or PR text. Use made-up data.
- **The contributor.** Absolute paths (`/Users/<name>/`, `/home/<name>/`, `C:\Users\`), machine
  and OS details ("on my MacBook"), private email addresses, employer names, internal hostnames
  and ticket ids from other organizations. Use repo-relative paths and neutral phrasing ("on a
  developer laptop").
- **Infrastructure.** Production server names, IPs, SSH targets, admin URLs not already public.

Useful sweep:

```bash
git diff <base>...HEAD | grep -nEi \
  'api[_-]?key|secret|token|password|bearer |BEGIN .*PRIVATE KEY|/Users/|/home/|C:\\Users|@gmail|\.local\b'
```

Report each leak as **file:line — what it is — what it exposes — what must happen** (delete,
rotate, rewrite). Anything live that reached a public commit must be rotated, however fast it
was removed. Do not rotate or rewrite history yourself; show the finding to the human.

## Pass 2 — fit to sign (non-blocking)

- Comments, commit messages, and PR text written for a stranger; no private shorthand.
- No junk: build output, IDE files (`.idea/`, `.kotlin/`), debug logging, commented-out code.
- Follows the repository's conventions (PR template, ticket key in title, license headers).

## Verdict

**BLOCKER** (any leak), **FIX** (should be fixed before a stranger sees it), **NICE**. End with
one line: "Fit to publish" or "Not fit: N blockers". Name what you could not check (binaries,
large fixtures) — an unchecked file reported as clean is the failure this skill exists to
prevent.
