# Threat model

## Assets

| Asset | Why it matters |
| --- | --- |
| Host filesystem and shell | The agent can read and write files and run commands. |
| Credentials in `~/.openclaw` | Channel tokens, provider keys, integration secrets. |
| The rest of the machine | A compromised agent should not reach your working profile, SSH keys, or other services. |
| Conversation history | Memory and sessions contain personal context. |
| Outbound identity | The bot speaks as you in the channels it is connected to. |

## Actors

- **You** — the operator. Trusted.
- **Approved senders** — paired accounts. Trusted to trigger the bot, not to be
  a security boundary.
- **Unknown senders** — untrusted. Can reach the bot if a channel accepts them.
- **Model output and fetched web content** — untrusted. A route for prompt
  injection.
- **The model provider** — receives prompts. Semi-trusted.

## Threats and controls

| Threat | Control | Config key | Check |
| --- | --- | --- | --- |
| Gateway reachable from the network | Bind loopback; reach it through an authenticated tunnel | `gateway.bind` | `gateway.bind` |
| Unauthenticated local or tunnel caller | Require a token | `gateway.auth.mode` | `gateway.auth.mode` |
| Real token committed to Git | Keep the placeholder; inject the token at deploy | `gateway.auth.token` | `check_secret_placeholders` |
| One sender's context leaking to another | Isolate DM sessions per peer | `session.dmScope` | `session.dmScope` |
| Tool call runs on the host | Sandbox tool execution | `agents.defaults.sandbox.mode` | `agents.defaults.sandbox.mode` |
| Sandbox reads the workspace | Deny workspace access | `agents.defaults.sandbox.workspaceAccess` | `agents.defaults.sandbox.workspaceAccess` |
| Over-broad tool access | Start from the messaging profile | `tools.profile` | `tools.profile` |
| Arbitrary command execution | Deny host exec | `tools.exec.security` | `tools.exec.security` |
| Exec slipping through without review | Require approval | `tools.exec.ask` | `tools.exec.ask` |
| Sandbox escape | Keep the escape hatch closed | `tools.elevated.enabled` | `tools.elevated.enabled` |

## Accepted risks

- **Shared authority.** Every approved sender can trigger an agent with the same
  tools. Pairing is not per-sender host isolation. Keep shared channels pointed
  at agents with minimal tools and no personal credentials.
- **Sandbox is not a wall.** It limits filesystem and process access; it is not
  a hard security boundary. Different trust levels need separate machines or OS
  users.
- **Provider exposure.** With a hosted model, prompts leave the machine. That is
  the trade for reliable tool use.

## Out of scope

- Securing the Windows host itself. That belongs to
  [`dev-setup-starter`](https://github.com/simpsonm09-org/simpsonm09-dev-setup).
- Multi-user, multi-tenant operation.
