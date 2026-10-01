# Backup and restore

The Gateway keeps everything that matters in `~/.openclaw`: configuration,
credentials, memory, sessions, and skills. Back it up before changes, and know
how to restore it.

## What to back up

| Path | Contents |
| --- | --- |
| `~/.openclaw/openclaw.json` | Gateway and agent configuration. |
| `~/.openclaw/` credential and channel state | Tokens and integrations. |
| Memory and session history | Personal context the agent relies on. |
| User skills | Locally authored skills. |

OpenClaw ships its own backup and restore commands. See
<https://docs.openclaw.ai/install/backups> for the current syntax, and prefer it
over a manual copy so the archive is consistent.

## Manual copy

If the built-in commands are not available:

```bash
tar -czf openclaw-backup-$(date +%Y%m%d).tgz -C ~ .openclaw
```

Treat the archive as a secret. It contains tokens.

## Restore

1. Stop the Gateway.
2. Restore `~/.openclaw` to the same user.
3. Re-apply `config/openclaw.json` if the configuration changed.
4. Start the Gateway and run:

   ```bash
   openclaw doctor
   openclaw security audit --deep
   ```

5. Confirm the channels reconnect and a message round-trips.

## Migration between machines

The homelab move is a restore: back up on the current machine, restore on the
homelab server, then walk the environment steps in
[`../machines/windows-wsl.md`](../machines/windows-wsl.md). Configuration is
machine-independent; only the environment notes differ.

## Verify the restore, not just the backup

A backup that has never been restored is a guess. Restore into a scratch user or
distro at least once and confirm `openclaw doctor` and a message round-trip.
