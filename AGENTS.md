# Agent notes

This repository holds configuration, documentation, and a small validator. It
does not install or run OpenClaw.

## Ground rules

- The Gateway is never bound to a network address. `gateway.bind` stays
  `loopback`; remote access is a tunnel in front of it.
- No secret is committed. `config/openclaw.json` keeps its placeholder token,
  and the validator enforces that. Real values live on the fork's `local`
  branch or in a local `.env`. See `docs/secrets.md`.
- Sandboxing is never turned off. `agents.defaults.sandbox.mode` stays `non-main`
  or `all`.
- Host exec stays denied until widened deliberately, one control at a time,
  with the security audit re-run after each change.

## Before proposing a change

- Run `python -m openclaw_homelab` against the configuration.
- Run `mise run lint` and `mise run test`.
- If the change weakens a control in `src/openclaw_homelab/validate.py`, update
  `docs/threat-model.md` in the same change, or do not make it.

## Layout

- `config/` holds the template configuration and its rationale.
- `docs/` holds the plan, architecture, threat model, machine notes, and
  runbooks.
- `docs/decisions.tsv` records decisions in `ts / phase / decision / why /
  evidence / result` form.
