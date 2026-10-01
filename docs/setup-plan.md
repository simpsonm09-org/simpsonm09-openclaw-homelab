# Setup plan

The phased rollout for a self-hosted OpenClaw gateway: first on this machine
(Windows + WSL2), then on the homelab server (Windows 10 + WSL2). Each phase
ends in a verifiable state. Do not start the next phase until the current one is
checked.

This repository stops at Phase 0. Phases 1 onward touch the machine and run only
when asked.

## Phase 0 — Prepare, no install

- Confirm WSL2 is current and `systemd=true` is set in `/etc/wsl.conf`, because
  the Gateway installs as a systemd user service. See
  [`machines/windows-wsl.md`](machines/windows-wsl.md).
- Decide the isolated environment. A dedicated WSL2 distro or a dedicated
  non-admin user is better than the profile you code in.
- Confirm Docker is reachable from inside WSL2 (Docker Desktop integration, or a
  Docker engine in the distro). The sandbox backend needs it.
- Put Tailscale on the **Windows host**, not inside WSL2.
- Pick the model provider and have its credential ready. Hosted models are the
  reliable choice for tool use; a local model is optional.

**Done when:** `wsl` runs, systemd is up (`systemctl is-system-running`), Docker
responds, and the gateway port `18789` is unused.

## Phase 1 — Install and verify

```bash
curl -fsSL https://openclaw.ai/install.sh | bash     # Linux / WSL2
openclaw onboard --install-daemon
openclaw doctor
openclaw gateway status
openclaw dashboard
```

On the homelab later, the same commands apply inside WSL2, or use the native
Windows paths described in [`machines/windows-wsl.md`](machines/windows-wsl.md).

**Done when:** `openclaw doctor` is clean and the Control UI answers on
`127.0.0.1:18789`.

## Phase 2 — Apply the hardened configuration

Deploy [`config/openclaw.json`](../config/openclaw.json) to
`~/.openclaw/openclaw.json` and replace the placeholder token with a real one
(see [`secrets.md`](secrets.md)). Then:

```bash
openclaw security audit
openclaw security audit --deep
```

Resolve critical findings before exposing anything.

**Done when:** the deep audit reports no critical findings, and
`python -m openclaw_homelab` still passes.

## Phase 3 — Sandbox the tools

Sandboxing is off by default, so confirm it took effect rather than assuming:

```bash
openclaw sandbox explain
openclaw sandbox list
```

The Gateway process itself stays on the host; only tool execution moves into the
sandbox. Keep the container's mounts narrow: no Docker socket, no home
directory, no credential paths.

**Done when:** `openclaw sandbox explain` shows the expected mode, scope, and
`workspaceAccess: none`.

## Phase 4 — Remote access

Choose the narrowest pattern that works, from the
[exposure runbook](runbooks/exposure.md):

| Pattern | Use when |
| --- | --- |
| Loopback + SSH tunnel | Just you, admin and debugging |
| Loopback + Tailscale Serve | Personal tailnet access, Gateway stays loopback |
| Tailnet/LAN bind | Private network, known devices; needs Gateway auth and a firewall allowlist |
| Public internet | Avoid |

Do not port-forward the Gateway. If remote access is required beyond loopback,
the identities in front of it must be authenticated.

**Done when:** an authorised connection succeeds, an unauthorised one is denied,
and no public route to port `18789` exists.

## Phase 5 — One channel

Start with one chat channel and a pairing policy.

- Use `dmPolicy: "pairing"` or a strict `allowFrom` list. Never `"open"`.
- Never combine a `"*"` allowlist with broad tool access.
- Require mentions in groups.

```bash
openclaw pairing approve <channel> <code>
```

**Done when:** only your account can trigger the bot, and a message from an
unknown sender does nothing.

## Phase 6 — Widen and automate

Only now, and one control at a time:

- Relax `tools.exec` for specific senders and commands, keeping `ask` on.
- Add skills from ClawHub selectively; they are third-party code.
- Add cron jobs and background tasks.
- Re-run `openclaw security audit --deep` after each change and record the
  result in [`decisions.tsv`](decisions.tsv).

## Deferred

- The container definition in [`services/openclaw/`](../services/openclaw/)
  lands after Phase 1 pins the image.
- `flint init` reconciles the tool pins in `mise.toml` once Flint is installed.
- Ruleset application (`repo-standard/scripts/apply-rulesets`) reports and stops
  while this repository is private on a free plan. Re-run it if the repository
  goes public.
