#!/usr/bin/env bash
set -euo pipefail
AVD_NAME="${AVD_NAME:-NexusMindLab}"

exec emulator -avd "$AVD_NAME" \
  -writable-system \
  -selinux disabled \
  -show-kernel \
  -no-snapshot-load \
  -qemu -s -append "nokaslr"
