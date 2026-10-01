# Secrets

## Rule

No secret is committed to this repository. The configuration ships a
placeholder, and the validator fails if the token field holds anything else.

## What lives where

| Secret | Lives in | Never in |
| --- | --- | --- |
| Gateway token | The deployed `~/.openclaw/openclaw.json`, and a local `.env` | This repository |
| Provider API keys | The Gateway's credential store on the machine | This repository |
| Channel bot tokens | The Gateway's channel configuration | This repository |

## The gateway token

Generate one:

```bash
openssl rand -hex 32
```

Then either:

- Replace `REPLACE_ME_GATEWAY_TOKEN` in the deployed
  `~/.openclaw/openclaw.json`, or
- Set `OPENCLAW_GATEWAY_TOKEN` in a local `.env` for the container path.

Either way, the repository copy keeps the placeholder.

## On the fork's local branch

Per [`repo-standard`'s governance](https://github.com/simpsonm09-org/simpsonm09-repo-standard/blob/main/docs/governance.md),
machine paths, secret wiring, and model overrides belong on the `local` branch of
the personal fork. That branch is the private divergence point. Nothing on
`local` is a pull-request candidate.

## Recovery

If a secret is committed by accident:

1. Rotate it first. Assume it is compromised the moment it is pushed.
2. Remove it from history, then force-push the branch if the rewrite is safe.
3. Re-run `openclaw security audit --deep` if the token was a gateway token.
