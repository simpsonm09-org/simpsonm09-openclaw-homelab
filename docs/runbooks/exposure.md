# Exposure runbook

How the Gateway is reached, and how to pull back if it is overexposed. Adapted
from the official
[exposure runbook](https://docs.openclaw.ai/gateway/security/exposure-runbook).

Expose the Gateway only after you can answer four questions: who can reach it,
how they are authenticated, which agents they can trigger, and which tools those
agents can use.

## Choose the pattern

Prefer the narrowest pattern that works.

| Pattern | Use when | Controls |
| --- | --- | --- |
| Loopback + SSH tunnel | Just you, admin and debugging | Keep `gateway.bind: "loopback"`, tunnel `127.0.0.1:18789` |
| Loopback + Tailscale Serve | Personal tailnet access | Gateway stays loopback; Tailscale authenticates the operator |
| Tailnet/LAN bind | Private network, known devices | Gateway auth, firewall allowlist, no public port-forward |
| Trusted reverse proxy | SSO in front of the Gateway | `trusted-proxy` auth, strict proxy IPs, header stripping |
| Public internet | Rare, high-risk | Identity-aware proxy, TLS, rate limits, strict allowlists |

**Do not port-forward the Gateway directly.** If public access is truly needed,
put an identity-aware proxy in front and make it the only network path.

## Pre-flight inventory

Record before any change:

- Host, OS user, and state directory (`~/.openclaw`).
- Gateway URL and bind mode (`gateway.bind`; default port `18789`).
- Auth mode and token source.
- Every enabled channel, and whether it accepts DMs, groups, or webhooks.
- Tool profile, sandbox mode, and elevated policy for each reachable agent.
- Backup location for `~/.openclaw/openclaw.json` and credentials.

## Baseline checks

```bash
openclaw doctor
openclaw security audit
openclaw security audit --deep
openclaw health
```

Resolve critical findings first. Accept warnings only when intentional and
recorded in [`../decisions.tsv`](../decisions.tsv).

## DM and group exposure

- Prefer `dmPolicy: "pairing"` or a strict `allowFrom` list over `"open"`.
- Never combine a `"*"` allowlist with broad tool access.
- Require mentions in groups unless the room is tightly controlled.
- Keep `session.dmScope` at `per-channel-peer` (or
  `per-account-channel-peer`) so DM sessions do not share context.

Pairing approves a sender to trigger the bot. It does not make that sender a
separate host security boundary.

## After each change

1. Re-run `openclaw security audit --deep`.
2. Confirm an authorised connection succeeds.
3. Confirm an unauthorised sender is denied.
4. Confirm no public route to `18789` exists.
5. Record the result in [`../decisions.tsv`](../decisions.tsv).

## Review checklist

- [ ] Gateway is loopback-only unless there is a documented reason.
- [ ] Non-loopback access has auth, a firewall, and no public direct route.
- [ ] DMs use pairing or allowlists, never open access.
- [ ] Groups require mentions or an explicit allowlist.
- [ ] Shared channels do not reach personal credentials.
- [ ] Non-main sessions run in sandbox mode.
- [ ] Host exec and elevated tools are denied or approval-gated.
- [ ] Critical audit findings are resolved.
