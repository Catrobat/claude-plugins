#!/usr/bin/env python3
"""Drive an Android emulator UI by element text, resource-id or content-desc via adb + uiautomator.

usage: ui.py STEP [STEP ...]
  "^Projects$"        tap the first node whose text matches the regex
  id:button_add       tap by resource-id (regex)
  desc:Back           tap by content-desc (regex)
  type:hello          type text into the focused field
  key:4               send a keyevent (4 = back, 66 = enter)
  sleep:3             wait 3 seconds
  shot:out.png        save a screenshot
  dump                print every visible text / id / desc (to find what to tap)
Exits 1 if a tap target is not found, after printing what is on screen.
"""
import os
import re
import shutil
import subprocess
import sys
import time


def adb_path():
    for home in (os.environ.get("ANDROID_HOME"), os.environ.get("ANDROID_SDK_ROOT")):
        if home and os.path.exists(os.path.join(home, "platform-tools", "adb")):
            return os.path.join(home, "platform-tools", "adb")
    return shutil.which("adb") or sys.exit("adb not found: set ANDROID_HOME or put platform-tools on PATH")


ADB = adb_path()
NODE = re.compile(r"<node [^>]*>")
BOUNDS = re.compile(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"')


def adb(*args, **kw):
    return subprocess.run([ADB, *args], check=True, **kw)


def dump():
    return adb("exec-out", "uiautomator", "dump", "/dev/tty", capture_output=True, text=True).stdout


def visible(xml):
    found = set()
    for attr in ("text", "resource-id", "content-desc"):
        found |= {f"{attr}={v}" for v in re.findall(attr + r'="([^"]+)"', xml)}
    return sorted(found)


def tap(pattern, attr="text"):
    xml = dump()
    for node in NODE.findall(xml):
        value = re.search(attr + r'="([^"]*)"', node)
        bounds = BOUNDS.search(node)
        if value and bounds and re.search(pattern, value.group(1)):
            x1, y1, x2, y2 = map(int, bounds.groups())
            adb("shell", "input", "tap", str((x1 + x2) // 2), str((y1 + y2) // 2))
            print(f"tapped {attr}={value.group(1)}")
            return
    print(f"NOT FOUND {attr}~{pattern}; on screen:", *visible(xml), sep="\n  ")
    sys.exit(1)


for step in sys.argv[1:]:
    kind, _, arg = step.partition(":") if re.match(r"^(id|desc|type|key|sleep|shot):", step) else ("", "", step)
    if kind == "sleep":
        time.sleep(float(arg))
        continue
    if kind == "shot":
        with open(arg, "wb") as f:
            f.write(adb("exec-out", "screencap", "-p", capture_output=True).stdout)
        print(f"screenshot {arg}")
        continue
    if step == "dump":
        print(*visible(dump()), sep="\n")
        continue
    if kind == "type":
        adb("shell", "input", "text", arg.replace(" ", "%s"))
    elif kind == "key":
        adb("shell", "input", "keyevent", arg)
    else:
        tap(arg, {"id": "resource-id", "desc": "content-desc"}.get(kind, "text"))
    time.sleep(2)
