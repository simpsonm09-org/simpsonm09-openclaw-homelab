# Configuration

`openclaw.json` is the hardened gateway configuration. It deploys to
`~/.openclaw/openclaw.json` on the machine that runs the Gateway.

It is a **template**, not a live file. The token field holds a placeholder, and
[the validator](../src/openclaw_homelab/validate.py) fails if it ever holds
anything else, so a real secret cannot be committed by accident. The real token
is injected at deploy time. See [`docs/secrets.md`](../docs/secrets.md).

The file is strict JSON rather than JSON5 so the standard library can parse it.
OpenClaw accepts comments in the deployed file; add them there, not here, so
`git diff` stays meaningful.

## What each control does

Every key below maps to a check in `check_controls` and to an entry in
[`docs/threat-model.md`](../docs/threat-model.md).

| Key | Value | Why |
| --- | --- | --- |
| `gateway.bind` | `loopback` | The Gateway never listens on a network interface. Remote access goes through an authenticated tunnel. |
| `gateway.auth.mode` | `token` | A token is required even for loopback-adjacent callers. |
| `session.dmScope` | `per-channel-peer` | Each direct-message peer gets its own session, so context does not leak between senders. |
| `agents.defaults.sandbox.mode` | `non-main` | Tool execution moves into a sandbox. Sandboxing is off by default. |
| `agents.defaults.sandbox.scope` | `session` | Each session gets its own environment. |
| `agents.defaults.sandbox.workspaceAccess` | `none` | The sandbox cannot read the host workspace. |
| `tools.profile` | `messaging` | Start from the narrowest useful tool set. |
| `tools.exec.security` | `deny` | Host exec is denied outright until it is widened on purpose. |
| `tools.exec.ask` | `always` | Any exec that is later allowed still needs approval. |
| `tools.elevated.enabled` | `false` | The sandbox escape hatch stays closed. |

## Widening

Change one control at a time, on the fork's `local` branch, and re-run
`openclaw security audit --deep` after each change. The invariants here describe
the baseline, not a permanent ceiling.
