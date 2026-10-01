# Rollback

Use this when the Gateway may be overexposed, or when a widened control misbehaves.
The goal is to return to the hard baseline, then re-widen deliberately.

## Step 1 — Close the controls

Deploy this configuration, replacing the placeholder token as usual:

```json
{
  "gateway": {
    "bind": "loopback"
  },
  "channels": {
    "whatsapp": { "dmPolicy": "disabled" },
    "telegram": { "dmPolicy": "disabled" },
    "discord": { "dmPolicy": "disabled" },
    "slack": { "dmPolicy": "disabled" }
  },
  "tools": {
    "exec": { "security": "deny", "ask": "always" },
    "elevated": { "enabled": false }
  }
}
```

This matches [`config/openclaw.json`](../config/openclaw.json) plus channel DMs
disabled.

## Step 2 — Remove the routes

1. Stop public forwarding, Tailscale Funnel, or reverse-proxy routes.
2. Confirm nothing answers on port `18789` from outside the machine.

## Step 3 — Rotate

Rotate the Gateway token and any affected integration credentials. A token that
was reachable should be treated as compromised.

## Step 4 — Review

1. Remove `"*"` and unexpected senders from allowlists.
2. Review recent audit logs, run history, tool calls, and config changes.
3. Re-run `openclaw security audit --deep`.
4. Re-enable access with the narrowest pattern that works, from the
   [exposure runbook](exposure.md).

## Step 5 — Record

Add a row to [`../decisions.tsv`](../decisions.tsv) with the trigger, the
action, and the result.
