---
name: simplify
description: >-
  Code-simplification pass over recently changed files: dead code, premature abstractions,
  needless indirection, redundant try/catch, over-defensive null checks, helpers used once,
  comments that say WHAT instead of WHY, tests that cannot fail. Never changes behavior. Use for
  "/simplify", "clean this up", or before committing (pr-quality runs it).
---

# /simplify — cleanup without behavior change

Scope is the latest churn, not the whole codebase: `git diff --name-only <base>...HEAD` plus
uncommitted changes.

## Look for

1. **Dead code** — unused functions, fields, imports, resources; commented-out blocks;
   unreachable branches.
2. **Premature abstraction** — an interface with one implementation, a helper with one caller,
   a wrapper type around one field.
3. **Needless indirection** — `val x = y; return x`, pass-through methods.
4. **Redundant error handling** — catch-and-rethrow, null checks on values that cannot be null
   (Kotlin non-null types, `@NonNull`), fallbacks the type system already rules out.
5. **Repetition** — the same three lines in three places want a helper (only at the third).
6. **Type smells** — unchecked casts, `!!` right after a nullable return, optional fields that
   are always set.
7. **Comment hygiene** — comments restating the code; stale comments from before a refactor.
8. **Test hygiene** — assertions that pass when the code is broken; mocks of the wrong layer.

## Do not touch

- Anything user-visible: layouts, strings, accessibility attributes, RTL handling.
- Security and privacy checks, input validation, permission handling.
- Tests that pin an external contract, even if verbose.
- Comments recording an invariant or a past bug — they prevent regressions.
- Generated code, license headers, build output.

## Process

1. For each candidate ask: would removing this change observable behavior? Yes → leave it.
2. After each batch, run the repository's own gate (see its `AGENTS.md`/`CLAUDE.md`). Anything
   red means the simplification was a regression — revert that one.
3. Keep patches small and focused per file.

## Report

Files touched, lines removed, lines added (should be fewer), and anything spotted but not
changed, with the reason. Do not commit — the caller or a human reviews the diff.
