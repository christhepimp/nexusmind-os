# NexusMind architecture

```
+----------------------------------------------------------+
|  You: natural language / voice / intent bus              |
+----------------------------------------------------------+
|  NexusMind Agent  (policy + tools + memory)              |
|    tools: sys.info, fs.list, proc.list, intent.dispatch  |
+----------------------------------------------------------+
|  NexusMind Runtime  (audit log, sandbox, allowlist)      |
+----------------------------------------------------------+
|  Android userspace  (init .rc, zygote, system_server)    |
+----------------------------------------------------------+
|  Linux kernel in the emulator  (ranchu / goldfish)       |
+----------------------------------------------------------+
|  QEMU on your host                                       |
+----------------------------------------------------------+
```

The AI is the **control plane**. Linux stays the **data plane** until we have earned the right to touch the kernel.

## Replacement order

1. **Shell UX** — conversation instead of launcher.
2. **Policy** — who may open a socket, install an apk, write `/data`.
3. **Supervisors** — wrap `init` services; restart them through the agent.
4. **Device model** — agent owns sensors/location as tools.
5. **Kernel experiments** — custom Image in a *second* AVD, never the daily lab.

## Agent loop (stub)

```
observe -> plan -> tool call -> verify -> remember -> reply
```

Every tool call is logged under `policies/` rules. If a call is not allowlisted, it is denied. An “AI OS” that can `rm -rf /` on a bad completion is just malware with extra steps.

## What we will not pretend

- The LLM is not a scheduler.
- The LLM is not a filesystem.
- The LLM does not become `swapper/0`.

Those stay Linux. The intelligence sits *above* them and gradually absorbs decisions humans used to click.
