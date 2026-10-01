# openclaw-homelab

Hardened configuration, validation, and runbooks for a self-hosted
[OpenClaw](https://openclaw.ai) gateway. OpenClaw is a personal AI agent that
runs on your own machine, meets you in the chat apps you already use, and gets
real tool access. This repository exists to make that deployment deliberate
instead of accidental.

**Status: scaffold only.** Nothing here installs or runs OpenClaw. The
repository holds the plan, the hardened configuration, the validator, and the
runbooks. The install happens in [Phase 1](docs/setup-plan.md).

Part of the `simpsonm09-org` fleet. The original lives in
[`simpsonm09-org/simpsonm09-openclaw-homelab`](https://github.com/simpsonm09-org/simpsonm09-openclaw-homelab);
work happens on a personal fork. See
[`repo-standard`](https://github.com/simpsonm09-org/simpsonm09-repo-standard) for the shared
CI, linting, security scanning, and branch governance.

## Why this exists

The risk in a personal agent is not the model. It is that the agent runs shell
commands, reads and writes files, and usually does so unattended, reachable from
a chat app. OpenClaw turns tools loose on the host unless sandboxing is
configured, and its own documentation says so. This repository pins the safe
defaults, proves them in CI, and records why each one is set.

## Layout

| Path | What it holds |
| --- | --- |
| `config/openclaw.json` | The hardened gateway configuration, as a template. |
| `src/openclaw_homelab/` | The validator that enforces the hardening invariants. |
| `tests/` | Behaviour tests for the validator. |
| `docs/setup-plan.md` | The phased rollout. |
| `docs/architecture.md` | Components and trust boundaries. |
| `docs/threat-model.md` | Assets, actors, and the control each one maps to. |
| `docs/secrets.md` | Where secrets live, and where they must not. |
| `docs/machines/` | Per-machine notes: Windows + WSL2 now, homelab later. |
| `docs/runbooks/` | Exposure, backup and restore, rollback. |
| `docs/decisions.tsv` | Decision log. |
| `services/openclaw/` | Deployment wiring. Deferred until Phase 1. |

## Documentation

Read [`docs/README.md`](docs/README.md) for the plan, architecture, threat model, runbooks, and machine notes.

## Validate the configuration

The validator has no third-party dependencies, so it runs anywhere Python 3.12
does.

```bash
python -m openclaw_homelab config/openclaw.json
```

The installed console script and the CI job run the same checks:

```bash
openclaw-homelab-validate
```

## Target

Windows with WSL2 now, on the current machine. The homelab server runs Windows
10 with WSL2, and the same artifacts move across unchanged. See
[`docs/machines/windows-wsl.md`](docs/machines/windows-wsl.md) for the WSL2
specifics and the migration notes.

## Local commands

```bash
mise install
pip install -e '.[test]'
mise run lint
mise run test
```

## License

MIT. See [`LICENSE`](LICENSE).
