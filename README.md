# NexusMind OS

**Goal:** study a rooted Android emulator (Linux underneath), then *incrementally* replace user-facing OS services with an AI-native control plane we design ourselves.

This is a **research lab**, not a claim that we can drop a new kernel into QEMU tomorrow and call it an AI operating system. Real OS replacement happens in layers: first userspace, then init/services, then (much later, if ever) kernel.

Repository: https://github.com/christhepimp/nexusmind-os

## What “AI as the OS” actually means here

The OS should *feel* like an intelligence, not a pile of apps:

- Intent instead of icons (“open my notes and summarize last week”)
- A single agent loop that owns scheduling, files, network policy, and UI
- Traditional Linux/Android kept as a **substrate** while NexusMind takes over the *policy* layer
- Slow replacement: each Linux daemon we understand can be wrapped, then swapped

You do **not** start by rewriting the Linux kernel. You start by owning PID 1’s children.

## Honest constraints

| Fantasy | Reality |
|---|---|
| “Replace Linux with AI inside the emulator” | Android *is* Linux + userspace. You can replace userspace services; replacing the kernel is a multi-year systems project. |
| Root = rewrite the kernel | Root = inspect, remount, load modules, patch userspace. Kernel swap needs a custom `Image` + boot args. |
| One weekend | Phase 0–1 is a weekend. A bootable custom kernel is months. An AI PID-1 is a research program. |

## Phase 0 — pick a rooted emulator (done research)

Best starting points for **root + Linux visibility**:

1. **Android Studio Emulator (AOSP / Google APIs images)**  
   Official, scriptable, `-writable-system`, QEMU gdb stub (`-qemu -s`).  
   Root paths: SuperSU / Magisk on writable system, [AERoot](https://github.com/quarkslab/AERoot) for Google Play images, [Root-Android-Emulator](https://github.com/peripheralmike/Root-Android-Emulator).

2. **Genymotion Desktop**  
   Rooted images available; good for inspection. Less kernel-hack friendly than goldfish/ranchu.

3. **BlueStacks 5**  
   Built-in Root Mode. Fine for apps, poor for kernel work.

4. **Waydroid on Linux host**  
   Not an emulator — Android userspace sharing the *host* kernel. Great if you already live in Linux.

**Recommended lab stack for this repo:** Android Studio AVD, API 29–33, **x86_64**, Google APIs (not Play if you want easy root), launched with:

```bash
emulator -avd NexusMindLab -writable-system -selinux disabled -show-kernel -no-snapshot-load -qemu -s -append "nokaslr"
```

Then `adb root && adb remount`.

See [docs/01-emulator-lab.md](docs/01-emulator-lab.md).

## Phase 1 — get *inside* Linux (not just `su`)

On a rooted emulator you should be able to:

```bash
adb shell
su
uname -a          # confirm kernel
cat /proc/version
ls /proc/1        # init / systemd-ish
ps -A
ls /sys /proc /dev
```

Next: pull kernel config if present (`/proc/config.gz`), map init (Android `init` + `.rc` files under `/system/etc/init`), list services with `getprop` / `lsof`.

This is the “Linux code inside Linux” step: **observe the running system**, don’t delete `/`.

## Phase 2 — wrap, don’t smash

NexusMind starts as a **userspace supervisor**:

- `nexusmind-agent` — LLM/tool loop (local model later; API stub now)
- `nexusmind-init` — optional sidecar next to Android `init`, not a replacement yet
- Policy files that decide which Linux tools the agent may run

The agent speaks *intents*. A thin runtime turns intents into `adb` / shell / file ops with an audit log.

Prototype lives in [`agent/`](agent/).

## Phase 3 — replace services one by one

Order of attack (safest first):

1. Launcher / SystemUI skin → conversational shell  
2. Notification + settings daemons → agent tools  
3. Package manager wrappers  
4. Network policy  
5. Only then consider a custom goldfish/ranchu kernel (see [fries/android-emulator-root](https://github.com/fries/android-emulator-root) for *how hard* custom emulator kernels are)

## Phase 4 — (long term) AI-native kernel research

Separate from this repo’s near-term code:

- Unikernel / seL4 / custom scheduler experiments  
- Model-in-the-loop resource allocation  
- Formal “do not panic the guest” tests

If we ever boot a non-Linux guest in the same QEMU machine, it will be a **new machine**, not a live rewrite of a running Android kernel.

## Repo layout

```
docs/                 research notes
agent/                Python stub for the AI control plane
labs/                 emulator launch scripts
policies/             what the agent is allowed to do
```

## Safety

- Lab only. Do not root random phones or attack devices you do not own.
- Do not commit Google keyboxes, Magisk modules of unknown origin, or exploit PoCs.
- Rooting tools that patch live kernel creds (AERoot, gdb_2_root) can **panic** the guest. Snapshot first.

## Status

- [x] Repo created
- [x] Emulator shortlist + launch notes
- [x] Agent stub + policy skeleton
- [ ] Working AVD checklist filled by you on your machine
- [ ] First intent: `sys.info` via adb
- [ ] Conversational shell over the emulator

## License

MIT. Research code. No warranty. The kernel will panic if you ask it to become sentient.
