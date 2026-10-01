# Windows + WSL2

Both the current machine and the homelab server run Windows with WSL2. The
Gateway runs inside the distro. The configuration is identical across machines;
the environment is not.

## Before installing

- **WSL2 must be current.** The Gateway installs as a systemd user service on
  Linux, and systemd inside WSL2 needs a recent WSL version.
- **Enable systemd** in the distro. Create or edit `/etc/wsl.conf`:

  ```ini
  [boot]
  systemd=true
  ```

  Then `wsl --shutdown` from Windows and reopen the distro. Confirm with:

  ```bash
  systemctl is-system-running
  ```

- **Do not run the Gateway as root.** Use a normal user in the distro.
- **Give the distro its own space.** A dedicated distro or user is better than
  the profile you develop in.

## Networking

- A Gateway bound to `127.0.0.1:18789` inside WSL2 is reachable from Windows on
  `localhost:18789` through WSL localhost forwarding. This is expected.
- **Never bind a wildcard address** (`0.0.0.0`). That exposes the Gateway on
  your LAN and defeats the whole posture.
- If the Gateway needs to reach a service on the Windows host or the LAN, check
  the distro's network mode. Mirrored networking behaviour differs by Windows
  version.

## Tailscale

Run Tailscale on the **Windows host**, not inside WSL2. WSL2's network is NAT'd,
which makes Tailscale-in-WSL awkward. The Windows host reaches the loopback
Gateway through localhost forwarding, so [`Tailscale Serve`](https://tailscale.com/kb/1242/tailscale-serve)
from the host is the clean path. Never use Funnel for this.

## Docker

The sandbox backend needs Docker reachable from inside the distro, either:

- Docker Desktop with WSL integration for the distro, or
- A Docker engine installed in the distro.

Confirm from inside WSL2 before Phase 3:

```bash
docker info
```

## Paths and line endings

- Windows path `D:\dev\...` is `/mnt/d/dev/...` in the distro.
- Keep repository files LF. `.gitattributes` already sets `* text=auto eol=lf`.
- Avoid running the Gateway against files under `/mnt/c` or `/mnt/d`; cross-filesystem
  access is slow and can change permissions.

## Homelab migration

The homelab server runs Windows 10 with WSL2. The move is a copy of
`~/.openclaw` plus the environment steps above. Two notes:

- Windows 10 reached end of support in October 2025. WSL2 still runs, but the
  host gets no security updates. Reconsider the host OS when building the
  homelab box, or keep the agent's blast radius small on that machine.
- Windows 10 WSL2 needs the Store version of WSL to get current systemd support.

## Native Windows alternative

OpenClaw also runs natively on Windows: the Windows Hub companion app, or the
PowerShell installer, with Microsoft Execution Containers for sandboxing. This
repository targets WSL2 to keep one set of artifacts across both machines. Use
the native path only if the WSL2 route is blocked.
