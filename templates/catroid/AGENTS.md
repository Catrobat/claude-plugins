# AGENTS.md — Catroid

Instructions for coding agents (Claude Code, Codex, Copilot, Cursor, …) and humans working on
Catroid. Read this before changing code.

## The project

Android app (Java + Kotlin) for the Catrobat visual programming language. JDK **21**,
`compileSdk 35`, `minSdk 28`. Main module: `catroid/`. Product flavors share one codebase; the
default flavor is `catroid` (`org.catrobat.catroid`).

- Default branch: **`develop`**. Never commit to it directly.
- PRs come from a **fork**. Push your branch to your fork remote, not to `Catrobat/Catroid`.
- PR title contains the Jira key (`CATROID-1234: …`). Follow `.github/PULL_REQUEST_TEMPLATE.md`
  and the [branch and commit guidelines](https://github.com/Catrobat/Catroid/wiki/Branch-and-Commit-Message-Guidelines).
- We work test-first (TDD). A change without a test that would fail without it is not done.

## Testing — what to run, and when

| level | command | needs | time |
|---|---|---|---|
| unit (JVM) | `./gradlew testCatroidDebugUnitTest --tests '*FooTest'` | nothing | seconds–minutes |
| all unit tests | `./gradlew testCatroidDebugUnitTest` | nothing | long |
| static analysis | `./gradlew detekt checkstyle pmd` | nothing | minutes |
| Android lint | `./gradlew lintCatroidDebug` | nothing | slow |
| compile device tests | `./gradlew compileCatroidDebugAndroidTestSources` | nothing | minutes |
| one device test | `./gradlew disableAnimations connectedCatroidDebugAndroidTest -Pandroid.testInstrumentationRunnerArguments.class=<FQCN>` | emulator | minutes |
| a device suite | same, with a suite class from `catroid/src/androidTest/java/org/catrobat/catroid/testsuites/` | emulator | slow (CI: tens of minutes) |

`disableAnimations` calls `adb` from `PATH`. Emulator setup: the `android-emulator` skill of
the Catrobat Claude plugin, or `.github/workflows/emulated_tests.yml` for what CI does.

### The local gate ("done")

1. Unit tests for the code you touched, plus any new ones — green.
2. `./gradlew detekt checkstyle pmd` — no new findings in changed files.
3. `./gradlew compileCatroidDebugAndroidTestSources` — device tests still compile.
4. **UI, stage, or Android-framework changes:** the device test classes you added or touched,
   run on an emulator. For broad UI changes, also `UiEspressoPullRequestTriggerSuite`.

### What CI runs — and what it does not

On every PR (`.github/workflows/main.yml`): APK build, unit tests, detekt/checkstyle/pmd/lint,
and the device suites `LocalHeadlessTestSuite`, `CatrobatTestRunner`,
`UiEspressoQuarantineTestSuite`, `UiEspressoRtlTestSuite` (API 35 emulator, slow).

**Not on PRs:** `UiEspressoPullRequestTriggerSuite` runs only after merge to `develop` and
nightly (`.github/workflows/ui.yml`). If your change can break the UI, run the relevant part of
it locally — otherwise the first signal is a red `develop` after merge.

## Conventions

- Kotlin for new code. Follow the existing style; detekt and checkstyle enforce it.
- Every new source file carries the AGPL license header (copy it from a neighbouring file).
- User-visible strings go in `res/values/strings.xml`; never hard-code them (translations, RTL).
- Do not commit `local.properties`, `.idea/`, `.kotlin/`, or build output.
- No real user data in tests, fixtures, or screenshots — Catrobat's users are largely children.
- Never put local paths, machine details, private emails, or secrets in commits or PR text.
