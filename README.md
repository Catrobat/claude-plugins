# Catrobat Claude plugins

Claude Code skills for contributing to Catrobat projects (Catroid, Catroweb, …). The core is a
**quality loop for pull requests**: the agent implements, runs the repo's own tests, waits for
CI on the exact commit, has a fresh independent agent review the diff cold, fixes what it finds,
and only then hands the PR to a human maintainer.

## Two parts

1. **Generic skills** (this repo, plugin `catrobat-dev`). They know *how* to work: the loop,
   the review, cleanup, publishing safety.
2. **Repo knowledge** (`AGENTS.md` in each project repo). It says *what* "tested" means there:
   commands, which tests need an emulator or browser, what CI does and does not run. Templates
   are in [`templates/`](templates/).

The skills read `AGENTS.md`, so one `pr-quality` works for an Android app and a Symfony site.
`AGENTS.md` also helps contributors who use Codex, Copilot, or Cursor instead of Claude.

## Skills

| skill | what it does |
|---|---|
| `/pr-quality` | Branch → local gate → commit → PR from your fork → CI on that SHA → cold review by a separate read-only Claude process → fix → repeat. Stops after 3 failed attempts. Never merges. |
| `/simplify` | Removes dead code and needless abstraction from the changed files, without behavior change. Run by `pr-quality` before every commit. |
| `/public-fit` | Checks a diff or PR text for secrets, real user data, and private contributor details before it goes public. |
| `/fix-bumps` | Diagnoses red Dependabot PRs (upstream regression / new lint rule / breaking change / flake) and opens a fixing PR. |
| `/android-emulator` | Creates and boots an emulator matching CI, runs Espresso suites, installs the app, and clicks through it by element text with `scripts/ui.py`. |

## Install

**For a project (recommended):** commit `templates/<project>/.claude/settings.json` to the
project repo. Everyone who opens the repo in Claude Code and trusts the folder is offered the
plugins listed there.

**Just for yourself:**

```
/plugin marketplace add Catrobat/claude-plugins
/plugin install catrobat-dev@catrobat
```

Requires a recent Claude Code — the cold review uses `claude -p --safe-mode --restricted`
(check `claude --help`).

## Recommended companion plugins

Enabled by the template settings; each is optional.

| plugin | why | for |
|---|---|---|
| [`ponytail`](https://github.com/DietrichGebert/ponytail) | Pushes the agent toward the smallest working change: reuse before writing, stdlib before dependencies. Fewer bloated PRs. | all |
| `mattpocock-skills` (official marketplace) | `/tdd` (red-green-refactor — Catroid requires TDD), `/diagnosing-bugs`, `/code-review`. | all |
| `playwright` (official marketplace) | Lets the agent open and click through the website in a real browser. | Catroweb |
| `php-lsp` (official marketplace) | Go-to-definition and diagnostics for PHP. | Catroweb |

## Emulator setup (Catroid)

What worked in practice, and what CI uses:

| | CI (`emulated_tests.yml`) | local, Apple Silicon | local, Linux/Windows |
|---|---|---|---|
| image | API 35, `x86_64`, google_apis | API 35 (33 also works), `arm64-v8a`, google_apis | API 35, `x86_64` (needs KVM / hypervisor) |
| device | default | `pixel_6` | `pixel_6` |
| flags | `-no-window -no-boot-anim -camera-* emulated` | `-no-snapshot -no-audio -no-boot-anim -gpu swiftshader_indirect` | same |

Full steps, including headless boot, waiting for boot, running a single test class, and driving
the UI: [`android-emulator` skill](plugins/catrobat-dev/skills/android-emulator/SKILL.md).

## What it costs

Each loop round runs the agent plus one review process. Contributors pay with their own Claude
plan or API key. Nothing in this repo needs a shared secret.

## Rolling out to a project

1. Copy `templates/<project>/AGENTS.md` (and `CLAUDE.md`, which just imports it) into the repo.
   Have a maintainer check the test commands.
2. Copy `templates/<project>/.claude/settings.json`.
3. Open a PR in the project. Try it on one real ticket: `/pr-quality`.
