# Secret placeholder guard

A user who changes the gateway token in the repository gets a specific violation back instead of a silent pass. The check keeps `config/openclaw.json` a template: the token field must hold the placeholder, and any other value is reported by key.

## Sub-features

- `secret-placeholder-pass` accepts `gateway.auth.token` holding `REPLACE_ME_GATEWAY_TOKEN` and reports nothing.
- `secret-detected` reports `gateway.auth.token` for any other value, including an empty string.

## How to get to it (user POV)

- Edit `gateway.auth.token` in a config file, then run the validator on it: `python -m openclaw_homelab path/to/openclaw.json`.
- The check runs on every validation, alongside the hardening controls, so a single command covers both families.

## Driving it with the CLI helper

Preconditions:

- The package is installed in `.venv` (see the skill's Launch section).
- The command runs from the repository root.

- **Pass.** The shipped `config/openclaw.json` keeps the placeholder. Run `.venv\Scripts\python.exe -m openclaw_homelab config/openclaw.json`. Exit `0`, no `gateway.auth.token` line on stderr.
- **Detected.** Copy the template, set `gateway.auth.token` to `"not-a-placeholder"`, and run the CLI on the copy. Exit `1`, and stderr carries `  - gateway.auth.token: must stay 'REPLACE_ME_GATEWAY_TOKEN' in the repository; inject the real token at deploy time (docs/secrets.md)`.
- **Helper.** Run `.venv\Scripts\python.exe .opencode/skills/verify/scripts/drive.py --repo-root . --out artifacts/verify/validator`. The `non_placeholder_token` case in `artifacts/verify/validator/evidence.json` records the exit code, stdout, and stderr for the detected path.
- **Proof.** Keep `artifacts/verify/validator/evidence.json` and read the `non_placeholder_token` entry; the value used is a deliberately non-placeholder string, never a real credential.

## Gotchas

- Only `gateway.auth.token` is guarded. Other token-shaped fields in the config are not checked by this validator, so a green pass does not mean every secret-shaped value is safe.
- The accepted placeholder literal is defined once as `TOKEN_PLACEHOLDER` in `src/openclaw_homelab/validate.py`; a change there changes what the guard accepts.
- The guard compares equality, so an empty token is a violation, not a pass.
- Do not put a real or realistic-looking secret into a fixture; use an obviously fake non-placeholder string.
