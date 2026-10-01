# OpenClaw service

Deployment wiring for the Gateway and its sandbox backend.

**Deferred.** The container definition lands after Phase 1 of
[`docs/setup-plan.md`](../../docs/setup-plan.md) verifies the install on the
target machine. The image reference and volume layout depend on what that
install produces, so this directory deliberately holds no invented compose file.

Until then, the install path is the documented one:

- Linux / WSL2: `curl -fsSL https://openclaw.ai/install.sh | bash`
- Container: <https://docs.openclaw.ai/install/docker>

## What lands here

- A compose file for the Gateway, once the image is pinned.
- A `.env` (git-ignored) copied from [`.env.example`](.env.example).
- The sandbox backend choice for this machine: Docker on the host, or the SSH
  backend if sandbox execution moves to a sibling host later.

## Reminder

The Gateway binds to loopback. If the compose file publishes a port, publish it
on `127.0.0.1` only. Never `0.0.0.0`.
