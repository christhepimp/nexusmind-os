# Emulator lab

## Recommended: Android Studio AVD

Why this one for NexusMind:

- Official QEMU (`ranchu` / goldfish)
- `-qemu -s` gives gdb on port 1234 — that is how tools like AERoot peek kernel memory
- `-writable-system` lets you remount `/system` after `adb root`
- You can later pass a custom `-kernel` image (hard, but documented)

### Create the AVD

Use **Google APIs** x86_64, not Play Store, for the first lab (Play images block `adb root`).

```bash
sdkmanager "platform-tools" "emulator" "system-images;android-33;google_apis;x86_64"
avdmanager create avd -n NexusMindLab -k "system-images;android-33;google_apis;x86_64" -d pixel_6
```

### Boot for surgery

```bash
emulator -avd NexusMindLab \
  -writable-system \
  -selinux disabled \
  -show-kernel \
  -no-snapshot-load \
  -qemu -s -append "nokaslr"
```

In another terminal:

```bash
adb wait-for-device
adb root
adb remount
adb shell uname -a
adb shell id
```

You want `uid=0(root)`.

### If you must use a Play image

Look at [quarkslab/AERoot](https://github.com/quarkslab/AERoot). It patches process credentials via gdb. It is fragile and version-specific. Snapshot the AVD first.

## Other emulators (when to use them)

| Product | Root | Kernel access | Use for NexusMind |
|---|---|---|---|
| Android Emulator (Studio) | Yes (APIs image / writable-system) | Best | Primary lab |
| Genymotion | Rooted images | Medium | App-level tests |
| BlueStacks 5 | Settings → Advanced → Root | Weak | Not for kernel work |
| Nox / LDPlayer / MuMu | Often a root toggle | Weak | Gaming, skip |
| Waydroid | Magisk scripts exist | Shares *host* kernel | If your daily driver is Linux |

## “Get in the Linux code” checklist

Once rooted:

```bash
adb shell su -c 'cat /proc/version'
adb shell su -c 'zcat /proc/config.gz | head'   # if present
adb shell su -c 'ls /system/etc/init'
adb shell su -c 'getprop | head'
adb shell su -c 'ps -A | head'
adb pull /system/etc/init labs/pulled-init || true
```

Android `init` is not systemd. Service definitions are `.rc` files. That is the first surface NexusMind can wrap.

## Custom kernel (later, not day one)

Goldfish/ranchu kernel trees live under AOSP (`kernel/goldfish` historically, now android-common kernels). Building a replacement `Image` and booting it with the emulator `-kernel` flag is the *only* honest way to “replace Linux” in this guest. Live rewriting of a running kernel from userspace is how you get a panic, not an AI OS.
