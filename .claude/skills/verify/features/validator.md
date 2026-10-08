# Validator

A user runs one command to check that an OpenClaw gateway configuration still holds the hardening invariants this repository requires. The command names the config it read, lists every violated key when the config is weak, and signals the result with its exit code.

## Sub-features

- `validate-default` reads `config/openclaw.json` with no path argument.
- `validate-explicit-path` reads the config file named as the first positional argument.
- `validate-pass` exits `0` and prints `<path>: ok` on stdout when every check holds.
- `validate-violations` exits `1` and prints a header plus one indented line per violated key on stderr.
- `validate-console-script` runs the same checks through the installed `openclaw-homelab-validate` entry point.

## How to get to it (user POV)

- From the repository root, run `python -m openclaw_homelab` to validate the shipped `config/openclaw.json`.
- Run `python -m openclaw_homelab path/to/openclaw.json` to validate a specific file.
- After `pip install -e ".[test]"`, run `openclaw-homelab-validate [path]` to reach the same checks through the console script.
- Read the exit code: `0` means clean, `1` means violations or an unreadable file.

## Driving it with the CLI helper

Preconditions:

- The package is installed in `.venv` (see the skill's Launch section).
- The command runs from the repository root.

- **Pass path.** Run `.venv\Scripts\python.exe -m openclaw_homelab config/openclaw.json`. Exit `0`, stdout is `config\openclaw.json: ok`, stderr is empty.
- **Default path.** Run `.venv\Scripts\python.exe -m openclaw_homelab` with no argument. Exit `0` and stdout names the default `config/openclaw.json` with `: ok`.
- **Violation path.** Copy the template, set `gateway.bind` to `"0.0.0.0"`, and run the CLI on the copy. Exit `1`, stdout is empty, and stderr carries `1 violation(s)` and `  - gateway.bind: must be 'loopback'; a wildcard bind exposes the Gateway on the network`.
- **Helper.** Run `.venv\Scripts\python.exe .claude/skills/verify/scripts/drive.py --repo-root . --out artifacts/verify/validator`. It drives the pass, default, and violation paths together and writes `artifacts/verify/validator/evidence.json`.
- **Proof.** Keep `artifacts/verify/validator/evidence.json`. A passing run prints `verify: pass` and exits `0`.

## Gotchas

- Violations go to stderr and `: ok` goes to stdout; capture both or the pass and fail cases look identical.
- Exit `1` does not by itself mean "config rejected": running the CLI on a path that does not exist raises an uncaught `FileNotFoundError` and also exits `1`, with a traceback on stderr instead of a violation list.
- The CLI has no `--help` or `--version`; the first positional argument is always treated as the config path, and there is no way to ask it for usage text.
- The default path is resolved from the package location, not the working directory, so `python -m openclaw_homelab` with no argument still reads the tracked `config/openclaw.json` from anywhere.
- A green unit test in `tests/test_validate.py` is not proof of the CLI; run the real command and read its exit code and streams.
