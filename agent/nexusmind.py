#!/usr/bin/env python3
"""NexusMind control-plane stub.

Talks to a rooted Android emulator over adb.
This is the start of the AI OS layer — intents in, audited shell out.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "policies" / "allowlist.json"


def load_policy() -> dict:
    if POLICY.exists():
        return json.loads(POLICY.read_text())
    return {"allowed_tools": ["sys.info"], "allowed_shell_prefixes": ["uname", "id", "getprop"]}


def adb(*args: str) -> str:
    cmd = ["adb", *args]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"adb failed: {cmd}")
    return proc.stdout.strip()


def tool_sys_info() -> dict:
    return {
        "id": adb("shell", "id"),
        "uname": adb("shell", "uname", "-a"),
        "fingerprint": adb("shell", "getprop", "ro.build.fingerprint"),
    }


TOOLS = {
    "sys.info": tool_sys_info,
}


def dispatch(intent: str) -> object:
    policy = load_policy()
    if intent not in policy.get("allowed_tools", []) and intent not in TOOLS:
        return {"denied": intent, "reason": "not in allowlist"}
    fn = TOOLS.get(intent)
    if not fn:
        return {"unknown_intent": intent}
    return fn()


def main() -> int:
    p = argparse.ArgumentParser(description="NexusMind OS agent stub")
    p.add_argument("intent", nargs="?", default="sys.info")
    args = p.parse_args()
    try:
        result = dispatch(args.intent)
    except FileNotFoundError:
        print("adb not on PATH. Install Android platform-tools.", file=sys.stderr)
        return 2
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
