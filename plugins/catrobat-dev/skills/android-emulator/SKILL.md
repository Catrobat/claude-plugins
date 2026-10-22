---
name: android-emulator
description: >-
  Create, boot, and drive an Android emulator for Catroid: run instrumented/Espresso suites,
  install a debug build, click through the app by element text or id, take screenshots, read
  logcat. Use for "run the UI tests", "test it on the emulator", "click through the app",
  "prove it works on a device", or any Catroid change that needs a device.
---

# android-emulator — prove it on a device

Unit tests run on the JVM; anything touching UI, Android framework classes, or the stage
needs a device. CI runs some device suites only after merge (see the repo's `AGENTS.md`), so
the local emulator is often the only proof a PR gets before review.

## Tools

The emulator, `adb`, and `avdmanager` live in the Android SDK. Put them on `PATH` once per
shell — Gradle's `disableAnimations` task calls bare `adb`:

```bash
export ANDROID_HOME="${ANDROID_HOME:-$HOME/Library/Android/sdk}"   # Linux: $HOME/Android/Sdk
export PATH="$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$PATH"
AVDM=$(ls "$ANDROID_HOME"/cmdline-tools/*/bin/avdmanager | head -1)
```

Catroid needs **JDK 21**. If Gradle picks another JDK, set `JAVA_HOME` explicitly.

## 1. Create the AVD (once)

Match CI where you can: CI uses **API 35, x86_64** (`reactivecircus/android-emulator-runner`).
On Apple Silicon use the `arm64-v8a` image of the same API level — x86_64 images do not run there.

```bash
ABI=$( [ "$(uname -m)" = arm64 ] && echo arm64-v8a || echo x86_64 )
"$ANDROID_HOME"/cmdline-tools/*/bin/sdkmanager "system-images;android-35;google_apis;$ABI"
echo no | "$AVDM" create avd -n catroid_test -k "system-images;android-35;google_apis;$ABI" -d pixel_6
```

API 33 also works if 35 is unavailable; note the API level in the PR's test recipe.

## 2. Boot headless and wait

Run in the background and log to a file:

```bash
emulator -avd catroid_test -no-window -no-snapshot -no-audio -no-boot-anim \
  -camera-back emulated -camera-front emulated -gpu swiftshader_indirect > emu.log 2>&1 &
adb wait-for-device
until [ "$(adb shell getprop sys.boot_completed | tr -d '\r')" = 1 ]; do sleep 5; done
```

First boot takes a few minutes. Drop `-no-window` if a human wants to watch. `adb devices` must
show exactly one device, or every `adb` call needs `-s emulator-5554`.

**Check `adb devices` before booting.** An emulator that is already running may belong to a
person or another agent mid-test: the same AVD refuses a second instance, and tapping on
someone else's emulator breaks their run. Create a second AVD (`catroid_test_2`) instead, and
only ever kill an emulator you started.

## 3. Run instrumented tests

```bash
./gradlew disableAnimations connectedCatroidDebugAndroidTest \
  -Pandroid.testInstrumentationRunnerArguments.class=<fully.qualified.TestClassOrSuite>
```

Run the **one test class** you changed first (minutes), then the suite the repo's `AGENTS.md`
names for your kind of change. Reports: `catroid/build/reports/androidTests/connected/`.

A test that fails once: re-run that class alone. Fails twice → it is a finding, not a flake.

## 4. Click through the app

```bash
./gradlew assembleCatroidDebug
adb install -r -g catroid/build/outputs/apk/catroid/debug/*.apk
adb shell monkey -p org.catrobat.catroid -c android.intent.category.LAUNCHER 1
```

Drive the UI with `scripts/ui.py` (next to this file) — it taps by visible text, resource-id,
or content-desc, so it does not break on screen size:

```bash
python3 <skill-dir>/scripts/ui.py dump                         # what is on screen
python3 <skill-dir>/scripts/ui.py "^Projects$" sleep:2 id:button_add shot:after.png
```

When a tap target is not found it prints everything visible, so you can correct the pattern.
The **stage** (a running Catrobat project) is one OpenGL surface — uiautomator sees no elements
there. Use screenshots, and coordinates only as a last resort.
Look at every screenshot you take; a test recipe that was never seen working is a guess.

- Clear logs before an action, read them after:
  `adb logcat -c` … `adb logcat -d | grep -iE 'catroid|AndroidRuntime|FATAL'`.
- App files: `adb shell run-as org.catrobat.catroid ls files/`.
- Use made-up accounts and data. Never log in with a real user's account for a test.

## 5. Clean up

```bash
adb emu kill
```

Delete screenshots and logs you do not attach to the PR. Screenshots that go into a PR must
contain no real user data.
