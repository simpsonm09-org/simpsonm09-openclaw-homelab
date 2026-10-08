---
name: verify
description: Drive the openclaw-homelab validator CLI (`python -m openclaw_homelab [path]`, entry point `openclaw-homelab-validate`) the way a user does and prove it accepts the shipped config and rejects weakened ones. Use when verifying a change to the hardening checks in src/openclaw_homelab/validate.py, the shipped config/openclaw.json, or the CI validation contract.
---

# Verify openclaw-homelab

openclaw-homelab is a dependency-free Python package whose user-facing surface is a validator CLI. It reads an OpenClaw gateway configuration and reports every check the configuration violates, exiting `0` when the config is clean and `1` when it is not. There is no server and no long-running process: verification means installing the package once, then running the real CLI over real configuration inputs and reading its exit code, stdout, and stderr.

## Launch

Run from the repository root. Create the virtual environment once and install the package with its test extra:

```bash
python -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[test]"
```

Inside WSL2 the interpreter is `.venv/bin/python`; substitute it for every `.venv\Scripts\python.exe` below.

There is nothing to keep alive. "Ready" means the CLI runs against the shipped template and reports it clean:

```bash
.venv\Scripts\python.exe -m openclaw_homelab config/openclaw.json
# config\openclaw.json: ok
```

Exit code is `0`. The installed console script runs the same checks after the editable install:

```bash
.venv\Scripts\openclaw-homelab-validate.exe config/openclaw.json
# config\openclaw.json: ok
```

Teardown deletes only scratch fixtures this run created; the `.venv` is reusable and the evidence under `artifacts/verify/` is kept.

## Doctor

One read-only check that decides whether the environment is worth driving. It confirms the pinned interpreter, that the package imports, and that the shipped template still passes:

```bash
.venv\Scripts\python.exe --version
# Python 3.12.10

.venv\Scripts\python.exe -m openclaw_homelab config/openclaw.json
# config\openclaw.json: ok
```

The version must be 3.12 (the package requires `>=3.12`), the command must exit `0`, and stdout must read `<path>: ok`. Anything else — wrong interpreter, `ModuleNotFoundError`, or a violation line — means the instance is not worth driving. Stop and redo Launch rather than building proof on it.

## Drive

Run the shipped helper from the repository root against the real CLI:

```bash
.venv\Scripts\python.exe .claude/skills/verify/scripts/drive.py --repo-root . --out artifacts/verify/validator
```

The helper shells out to `python -m openclaw_homelab` (the interpreter running the helper, with `src/` on `PYTHONPATH`) over four inputs and records each one's exit code, stdout, and stderr:

- `config/openclaw.json` as shipped, passed explicitly — expect exit `0` and `: ok`.
- no path argument, so the CLI falls back to its default config — expect exit `0` and `: ok`.
- a copy with `gateway.bind` widened to `0.0.0.0` — expect exit `1` and a `gateway.bind` line on stderr.
- a copy with a non-placeholder token — expect exit `1` and a `gateway.auth.token` line on stderr.

It writes `artifacts/verify/validator/evidence.json` (and the two fixture configs under `fixtures/`) and exits non-zero when any expected outcome is wrong.

To drive one case by hand, write a config with one control widened and run the CLI on it. Violations print to stderr:

```bash
.venv\Scripts\python.exe -m openclaw_homelab path/to/weakened.json
# path/to/weakened.json: 1 violation(s)
#   - gateway.bind: must be 'loopback'; a wildcard bind exposes the Gateway on the network
```

## Evidence

Proof artifacts go to `artifacts/verify/validator/` and survive teardown. `artifacts/` is gitignored.

- The pass path is proven by the real exit code `0` plus `: ok` on stdout and an empty stderr, not by reading `validate_config` in a unit test.
- The rejection path is proven by the real exit code `1` plus the violated key named on stderr, for both a hardening control and the secret guard.
- The action and the resulting state are both recorded: the exact argv, the exit code, stdout, and stderr for each case.
- A change to a check in `src/openclaw_homelab/validate.py` is proven by a config that trips that check and an observed violation line, not by the shipped template still passing.
- The default-config path (`python -m openclaw_homelab` with no argument) is exercised separately, because it is the command AGENTS.md and CI rely on.
- A non-zero exit alone is not proof of rejection: verify the stderr text, since an unreadable file also exits `1` (see Gotchas).

## Cleanup

The validator is a short-lived process, so there is no server to stop. Remove only the scratch fixtures a failed or partial run may have left outside the evidence directory; keep `artifacts/verify/validator/` and its `evidence.json` and `fixtures/`. Deleting the `.venv` is optional and unrelated to the proof.

## Helpers

`scripts/drive.py` is the driver. Invoke it as shown in Drive. It accepts `--repo-root` (default `.`) and `--out` (default `artifacts/verify/validator`, relative to `--repo-root`), creates the fixture configs, prints the evidence as JSON, and returns non-zero on a failed assertion.
