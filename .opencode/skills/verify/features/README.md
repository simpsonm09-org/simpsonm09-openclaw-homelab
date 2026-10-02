# openclaw-homelab verification map

This directory is the maintained source for verifying the user-facing behavior of openclaw-homelab. Read the index before driving the app, then use the matching feature file as the recipe.

## Baseline preconditions

- The package is installed in `.venv` with its test extra (see the skill's Launch section).
- The pinned interpreter is Python 3.12; `.venv\Scripts\python.exe --version` reports it.
- The shipped `config/openclaw.json` passes with exit `0`.
- Every drive uses a config input this run controls; never weaken the tracked `config/openclaw.json` in place.
- Write proof under `artifacts/verify/<feature>/`.

## Driving conventions

- Start every recipe from the repository root.
- Prefer the real CLI, `python -m openclaw_homelab [path]`, over importing functions from the package.
- Record the exit code, stdout, and stderr of every invocation; the exit code alone is ambiguous.
- Pass checks print `<path>: ok` to stdout; violations print a header and an indented list to stderr.
- Run the shipped helper `scripts/drive.py` for the multi-case pass; run a single `python -m openclaw_homelab <path>` for a hand probe.
- Keep proof artifacts during cleanup.

## Proof and skip reporting

- Capture the action (the argv) and the resulting state (exit code, stdout, stderr), not only the final line.
- A pass is proven by exit `0` with `: ok` and an empty stderr.
- A rejection is proven by exit `1` with the violated key named on stderr.
- Record the feature ID and the exact config input used with every artifact.
- Report an unreachable path with the attempted command and the unmet precondition.
- Do not report a skipped entry point, such as the console script, as verified through a different path.

## Feature entry contract

Each feature file starts with an H1 title and one paragraph of user-visible behavior, then exactly four H2 sections: `Sub-features`, `How to get to it (user POV)`, `Driving it with <harness>`, and `Gotchas`.

## Features

- [Validator](./validator.md) covers running the CLI against a config, the pass and violation paths, exit codes, and the default config.
- [Secret placeholder guard](./secret-placeholder.md) covers the committed-token check and its single observed violation.
